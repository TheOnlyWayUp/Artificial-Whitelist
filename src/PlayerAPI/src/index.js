const mc = require('minecraft-protocol')
const express = require("express");
const fs = require('fs');

let config = JSON.parse(fs.readFileSync(process.env.PLAYER_API_CONFIG_FILE));
const app = express();

let HOST = config.server.address
let PORT = config.server.port
let EXPRESS_PORT = config.serve.port
let EXPRESS_AUTH = config.authorization

let credentials = config.accounts
let usernames_to_passwords = {}
credentials.forEach(element => {
    let username = element.split(":")[0]
    let password = element.split(":")[1]
    usernames_to_passwords[username] = password
})

let joined_accounts = [];
let sitting_out = [];
let usernames_to_bot = {};

app.use(function (req, res, next) {
    if (req.headers.authorization != EXPRESS_AUTH) {
        return res.status(403).json({ error: 'Forbidden' });
    }
    next();
});
// https://stackoverflow.com/a/46094495


app.get("/join_all/", (req, res) => {
    credentials.forEach(account => {
        let username = account.split(":")[0]
        let password = account.split(":")[1]

        try {
            let bot = mc.createClient({
                host: HOST,
                port: PORT,
                username: username,
                password: password,
                auth: 'mojang'
            })

            usernames_to_bot[username] = bot
            joined_accounts.push(username)
        } catch {

        }
    })
    res.status(200).send({ "success": true, "data": { "users": Object.keys(usernames_to_passwords) } })
})

app.get("/sit_out", (req, res) => {
    let username = joined_accounts.pop();
    if (username == undefined) {
        res.status(422).send({ "success": false, "data": { "message": "No bots are filling in!" } })
        return
    }
    try {
        let bot = usernames_to_bot[username];
        delete usernames_to_bot[username]
        bot.end()
        sitting_out.push(username)
    } catch {
        res.status(500).send({ "success": false, "data": { "message": "There was an error." } })
    }


    res.status(200).send({ "success": true, "data": { "username": username } })
})

app.get("/fill_in", (req, res) => {
    let username = sitting_out.pop()
    if (username == undefined) {
        res.status(422).send({ "success": false, "data": { "message": "No bots are sitting out!" } })
        return
    }

    try {
        let password = usernames_to_passwords[username]

        usernames_to_bot[username] = mc.createClient({
            host: HOST,
            port: PORT,
            username: username,
            password: password,
            auth: 'mojang'
        })

        joined_accounts.push(username)
    } catch {
        res.status(500).send({ "success": false, "data": { "message": "There was an error." } })
    }

    res.status(200).send({ "status": true, "data": { "username": username } })
})

app.listen(EXPRESS_PORT, () => {
    console.log(`App listening on port ${EXPRESS_PORT}`);
});