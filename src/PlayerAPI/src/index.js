const mc = require('minecraft-protocol')
const express = require("express");
const fs = require('fs');

let config = JSON.parse(fs.readFileSync(process.env.PLAYER_API_CONFIG_FILE));
const app = express();

let HOST = config.server.address
let PORT = config.server.port
let EXPRESS_PORT = config.serve.port
let EXPRESS_AUTH = process.env.API_AUTH_KEY

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
    // Middleware to check if Authorization Header matches Auth Key.
    if (req.headers.authorization != EXPRESS_AUTH) {
        return res.status(403).json({ error: 'Forbidden' });
    }
    next();
});
// https://stackoverflow.com/a/46094495

app.get("/maxlen/", (req, res) => {
    // Max number of bots that can join the server.
    res.status(200).send({ "MAX_SIZE": credentials.length })
})

app.get("/join_all/", (req, res) => {
    // Prompt all the bots to join the server.
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
    // Ask a bot to temporarily leave the server, returning a boolean success and the bot's username.
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
    // Ask a bot sitting out to rejoin the server, returning a boolean success and the bot's username.
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

process.on('SIGTERM', () => {
    // Graceful shut down
    console.log('SIGTERM received, shutting down...');
    server.close()
    // https://github.com/expressjs/express/issues/1366
});

var server = app.listen(EXPRESS_PORT, () => {
    console.log(`App listening on port ${EXPRESS_PORT}`);
});