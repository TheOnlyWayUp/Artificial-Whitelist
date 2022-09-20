"""API to store and correlate Player Usernames and IP Addresses."""

import os, json
from typing import Dict, List
from fastapi import FastAPI, Header, Depends
from fastapi.exceptions import HTTPException

# --- Parsing Config --- #

STATS_API_CONFIG_PATH = os.getenv("STATS_API_CONFIG_PATH")
assert (
    STATS_API_CONFIG_PATH
), "Set the STATS_API_CONFIG_PATH Environment Variable before running."
with open(STATS_API_CONFIG_PATH) as config_file:
    config = json.load(config_file)

BIND_ADDRESS = config["bind"]["address"]
BIND_PORT = config["bind"]["port"]

DATABASE_PATH = config["db_file"]
AUTHORIZATION = os.environ["API_AUTH_KEY"]


def check_auth(authorization: str = Header(...)):
    """Auth Dependency to check authorization header with auth key."""
    if authorization != AUTHORIZATION:
        raise HTTPException(status_code=403, detail="Forbidden")


app = FastAPI(dependencies=[Depends(check_auth)])

try:
    with open(DATABASE_PATH, "r") as handler:
        ...
except:
    # create file if not exist
    with open(DATABASE_PATH, "w") as handler:
        json.dump({}, handler)

# --- #


@app.get("/log/{username}/{address}")
def log(username: str, address: str):
    """Log a username joining from an IP Address, both arguments provided in the route."""
    with open(DATABASE_PATH) as handler:
        old_data: Dict[str, List[str]] = json.load(
            handler
        )  # usernames: list of ip addresses
    data = set(old_data.get(username, []))
    data.add(address)
    data = list(data)
    old_data[username] = data
    with open(DATABASE_PATH, "w") as handler:
        json.dump(old_data, handler)
    return 200


@app.get("/similar/{username}")
def similar(username: str):
    """Return a list of usernames of Minecraft Accounts that've joined from the same IP as the one provided in the route."""
    with open(DATABASE_PATH) as handler:
        old_data: Dict[str, List[str]] = json.load(
            handler
        )  # usernames: list of ip addresses
    new_data: Dict[str, List[str]] = {}  # ip_address, list of usernames
    for username, addresses in old_data.items():
        for ip_address in addresses:
            d = set(new_data.get(ip_address, []))
            d.add(username)
            new_data[ip_address] = list(d)
    to_return = set()
    for ip_address in old_data[username]:
        for other_user in new_data[ip_address]:
            to_return.add(other_user)
    return list(to_return)


# --- #

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=BIND_ADDRESS, port=BIND_PORT)
