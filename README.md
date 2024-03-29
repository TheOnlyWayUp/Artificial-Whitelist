Minecraft Artificial Whitelist
---
Leverage multiple user accounts to:
- Enforce an artificial whitelist on a server, join via a proxy
- Reserve a spot on busy servers
- Prevent malicious users from joining (This was our usecase on the LiveOverflow LetsPlay Server)

## Includes
- Discord bot, for whitelisting/blacklisting users, and over-all management
- Developer-friendly APIs for Statistics and the Player Manager, so you can control it programmatically via your code as well
- Minecraft proxy server, allowing seamless usage for end users

Supports docker-compose. Up in one command.

Code is a performant, function POC, developed under tight time-constraints.

---


LiveOverflow Server Proxy
------------
A project that enforces a sort of 'artificial whitelist' on the LiveOverflow Server, allowing the user to enforce a blacklist/whitelist.

Components
- Proxy Server - A TCP Proxy that makes sure a user is authorized to join the server by extracting their username from unencrypted packets
- PlayerAPI - An API that allows the Proxy to 'fill in' and 'sit out' for users with Minecraft Bots. The server is filled to its maximum player limit with bots, and when an actual user has to join, one of the bots leaves.
- StatsAPI - Allows correlating a Minecraft Account to other accounts that've logged in from similar areas.
- Discord Bot - Allows the Proxy to be controlled (live changes) from a discord server. Users can be whitelisted, the proxy mode (whitelist/blacklist) can be changed, etc.

User joins the Proxy -> Proxy stores their Username -> Forwards Packets -> Proxy checks whether encryption has been enabled or not (presence of c->s encryption response packet) -> If encrypted, username is exchanged for UUID and checked with Proxy Mode and Player List. -> If player is not allowed, their connection is closed -> Else, a bot is asked to leave for them and the connection is delayed -> Packets continue to be forwarded -> On leave, the bot is asked to rejoin

Simply Put,

![Image describing join process (simplified)](https://i.imgur.com/u1mqq7s.png)

Flow

![Flowchart describing what happens during the lifecycle of a connection.](LO-Proxy-Flow.svg)
