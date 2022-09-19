import os
from fastapi import FastAPI, Depends, Header
from fastapi.exceptions import HTTPException
from config import API_CONFIG, get_data, set_data

AUTHORIZATION = os.environ['API_AUTH_KEY']


def check_auth(authorization: str = Header(...)):
    if AUTHORIZATION != authorization:
        raise HTTPException(status_code=403, detail="Forbidden")


app = FastAPI(dependencies=[Depends(check_auth)])

# --- #


@app.get("/players")
def get_players():
    return get_data().get("players", [])


@app.get("/mode")
def get_mode():
    return get_data().get("mode", "")


@app.get("/players/{players}")
def set_players(players: str):
    data = get_data()
    data["players"] = players.split(",")
    set_data(**data)


@app.get("/mode/{mode}")
def set_mode(mode: str):
    data = get_data()
    data["mode"] = mode
    set_data(**data)


# --- #

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, host=API_CONFIG["bind"]["address"], port=API_CONFIG["bind"]["port"]
    )
