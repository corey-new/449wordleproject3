import redis
import dataclasses
import json
import toml
import secrets
import hashlib
import uuid

from quart import Quart, g, request, abort, make_response
from quart_schema import (
    tag,
    validate_request,
    QuartSchema,
    validate_response,
)
from random import randint
from typing import Tuple

app = Quart(__name__)
QuartSchema(app)

app.config.from_file("./etc/wordle.toml", toml.load)

# ---------------------------------------------------------------------------- #
#                                  dataclasses                                 #
# ---------------------------------------------------------------------------- #
@dataclasses.dataclass
class Error:
    error: str


@dataclasses.dataclass
class DC:
    username: str
    game_id: str
    remaining_guesses: int
    status: str


# ---------------------------------------------------------------------------- #
#                                 helper funcs                                 #
# ---------------------------------------------------------------------------- #

async def _get_redis_db():
    r = redis.Redis(host='localhost',port=6379,db=0)
    return r



# --------------------- add game score --------------------- #
@app.route("/games/<string:game_id>", methods=["POST"]) #todo: fix route and args
@tag(["games"])
@validate_request(DC, 201)
@validate_response(Error, 400)
async def add_game_score(data):

    _dc = dataclasses.asdict(data)

    username = _dc["username"]
    game_id = _dc["game_id"]
    remaining_guesses = _dc["remaining_guesses"]
    status = _dc["status"]

    r = _get_redis_db()

    # adds score for this game to redis
    if status != "In Progress":
        if status == "won":
            r.hset(username, game_id, 1+remaining_guesses)
        elif status == "lost":
            r.hset(username, game_id, 0)

        r.hset("average_score", username, 0) # ensures that there is an entry for average_score.  doesnt matter that we're setting it to 0, since we're recalculating it now anyway

        playerscores = r.hgetall(username)
        totalscore = 0
        for key, value in playerscores.items():
            totalscore = totalscore + value

        r.hset("average_score", username, totalscore/len(playerscores)) 
    

# ---------------------------- retrieve game score --------------------------- #
@app.route("/games/<string:game_id>", methods=["GET"]) #todo: fix route and args
@tag(["games"])
@validate_response(Error, 401)
@validate_response(Error, 404)
async def get_game_state(username, game_id):
    
    r = _get_redis_db()

    gamescore = r.hget(username, game_id)

    return {
        "username": username,
        "game_id": game_id,
        "score": gamescore,
    }, 200


# ---------------------------- retrieve user average score --------------------------- #
@app.route("/games/<string:game_id>", methods=["GET"]) #todo: fix route and args
@tag(["games"])
@validate_response(Error, 401)
@validate_response(Error, 404)
async def get_game_state(username):
    
    r = _get_redis_db()

    averagescore = r.hget("average_score", username)

    return {
        "username": username,
        "score": averagescore,
    }, 200


# ---------------------------- retrieve top 10 average scorers --------------------------- #
@app.route("/games/<string:game_id>", methods=["GET"]) #todo: fix route and args
@tag(["games"])
@validate_response(Error, 401)
@validate_response(Error, 404)
async def get_game_state(username):
    
    r = _get_redis_db()

    averagescores = r.hgetall("average_score")
    
    averageScoresSorted = sorted(averagescores.items(), key=lambda x: x[1], reverse=True)

    x = 10
    topTen = {}
    for i, (key, value) in enumerate(averageScoresSorted.items()):
        entries[key] = value
        if i == x-1:
            break


    return json.dumps(topTen)