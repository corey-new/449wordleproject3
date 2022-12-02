import databases
import dataclasses
import sqlite3
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
class Guess:
    guess: str


@dataclasses.dataclass
class CreatedGame:
    game_id: str
    remaining_guesses: int = 6
    status: str = "In Progress"


# ---------------------------------------------------------------------------- #
#                                error handlers                                #
# ---------------------------------------------------------------------------- #
@app.errorhandler(400)
async def bad_request(e):
    return {"error": f"Bad Request: {e.description}"}, 400


@app.errorhandler(401)
async def unauthorized(e):
    response = await make_response({"error": f"Unauthorized: {e.description}"}, 401)
    response.status_code = 401
    response.headers["WWW-Authenticate"] = 'Basic realm="User Login"'
    return response


@app.errorhandler(404)
async def not_found(e):
    return {"error": f"Not Found: {e.description}"}, 404


# ---------------------------------------------------------------------------- #
#                               helper functions                               #
# ---------------------------------------------------------------------------- #
async def _get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = databases.Database(app.config["DATABASES"]["GAMES"])
        await db.connect()
    return db

@app.teardown_appcontext
async def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        await db.disconnect()

async def _get_random_word():
    with open("./share/correct.json") as file:
        data = json.load(file)
        rand_index = randint(0, len(data) - 1)
        return data[rand_index]


async def _check_string(guess: str, goal: str) -> Tuple[str, str]:

    guess = guess.lower()

    if guess == goal:
        return (goal, "?????")

    # helper function to replace a character in an index of a string
    def replace_idx(s: str, idx: int, letter: str) -> str:
        return s[:idx] + letter + s[idx + 1 :]

    # create a hashmap of goal string and letter count
    goal_cnt = {}
    for letter in goal:
        goal_cnt[letter] = goal_cnt.get(letter, 0) + 1

    correct_spot = "?????"
    incorrect_spot = "?????"

    # first pass to check for correct spot which deals with duplicates,
    # ex: guess = "hello", goal = "world", we dont want to count the first 'l'.
    for i in range(len(guess)):
        if guess[i] == goal[i]:
            correct_spot = replace_idx(correct_spot, i, guess[i])
            goal_cnt[guess[i]] -= 1

    # second pass to check for incorrect spot
    for i in range(len(guess)):
        if guess[i] != goal[i] and goal_cnt.get(guess[i], 0) > 0:
            incorrect_spot = replace_idx(incorrect_spot, i, guess[i])
            goal_cnt[guess[i]] -= 1

    return (correct_spot, incorrect_spot)


# ---------------------------------------------------------------------------- #
#                                  api routes                                  #
# ---------------------------------------------------------------------------- #
# -------------------------------- create game ------------------------------- #
@app.route("/games/create", methods=["POST"])
@tag(["games"])
@validate_response(CreatedGame, 201)
@validate_response(Error, 400)
async def create_game():
    """Create a new game for a user with a random word."""

    myuuid = str(uuid.uuid4())

    game = {}
    game["secret_word"] = await _get_random_word()
    game["username"] = request.authorization.username
    game["game_id"] = myuuid
    db = await _get_db()

    # create new row in game
    try:
        id = await db.execute(
            """
            INSERT INTO games(game_id,secret_word, username)
            VALUES(:game_id, :secret_word, :username)
            """,
            game,
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)

    game_state = {
        "game_id": game["game_id"],
        "remaining_guesses": 6,
        "status": "In Progress",
    }
    # create new row in game_states
    try:
        id = await db.execute(
            """
            INSERT INTO game_states(game_id, remaining_guesses, status)
            VALUES(:game_id, :remaining_guesses, :status)
            """,
            game_state,
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)

    return game_state, 201, {"Location": f"/games/{game['game_id']}"}


# ---------------------------- retrieve game state --------------------------- #
@app.route("/games/<string:game_id>", methods=["GET"])
@tag(["games"])
@validate_response(Error, 401)
@validate_response(Error, 404)
async def get_game_state(game_id):
    """Retrieve the history of a game or the result if it is over."""
    db = await _get_db()

    # we need all rows in game_history for the game_id
    # join with game_states and games to get secret_word, status, and remaining_guesses
    # [0] = game_id, [1] = guess, [2] = secret_word, [3] = status,
    # [4] = remaining_guesses in guess for history, [5] = remaining guesses in game_states
    # [6] = username corresponding to this game (for auth purposes)
    query = """
        SELECT
            game_states.game_id, game_history.guess, games.secret_word,
            game_states.status, game_history.remaining_guesses, 
            game_states.remaining_guesses, games.username
        FROM game_states
            INNER JOIN game_history ON game_states.game_id = game_history.game_id
            INNER JOIN games ON game_states.game_id = games.game_id
        WHERE game_states.game_id = :game_id
        """

    game_states = await db.fetch_all(
        query,
        values={"game_id": game_id},
    )

    app.logger.info(query)

    # check if this user is performing a lookup on a game they started
    if game_states and request.authorization.username != game_states[0][6]:
        # not this user's game
        abort(401, "You cannot access this game.")

    if game_states:
        response = []
        for state in game_states:
            if state[3] == "In Progress":
                evaluation = await _check_string(state[1], state[2])
                state_info = {
                    "game_id": state[0],
                    "guess": state[1],
                    "remaining_guesses": state[4],
                    "correct_spots": evaluation[0],
                    "incorrect_spots": evaluation[1],
                }
                response.append(state_info)
            elif state[3] == "won" or state[3] == "lost":
                return {
                    "game_id": state[0],
                    "status": state[3],
                    "remaining_guesses": state[5],
                }, 200
        return response, 200
    else:
        abort(404, "No game history found for given game id.")


# --------------------- make a guess / update game state --------------------- #
@app.route("/games/<string:game_id>", methods=["POST"])
@tag(["games"])
@validate_request(Guess)
@validate_response(Error, 400)
async def check_guess(data, game_id):
    """Make a guess for a game with a given game_id. Returns updated game state."""

    guess = await request.get_json()
    guess = guess["guess"]

    if len(guess) != 5:
        abort(400, "Guess must be 5 letters long.")

    db = await _get_db()

    # check if the user can access this game
    # TODO: can combine this SELECT with the one that fetches (secret_word, remaining_guesses)
    # TODO: to not have to query DB multiple times, but for now its ok
    uname = await db.fetch_val(
        "SELECT username FROM games WHERE game_id = :game_id",
        values={"game_id": game_id},
    )
    if request.authorization.username != uname:
        abort(401, "You cannot access this game.")

    # perform lookup in db table "game_states" to check if game is in progress
    query = "SELECT game_states.status FROM game_states WHERE game_states.game_id = :game_id"
    status = await db.fetch_val(
        query,
        values={"game_id": game_id},
    )

    # if finished, then return number of guesses and game status
    if status != "In Progress":
        query = "SELECT game_states.remaining_guesses FROM game_states WHERE game_states.game_id = :game_id"
        guesses = await db.fetch_val(
            query,
            values={"game_id": game_id},
        )
        app.logger.info(query)
        return {"remaining_guesses": guesses, "status": status}

    # perform lookup in db table "valid_words" to check if guess is valid
    query = "SELECT EXISTS(SELECT 1 FROM valid_words WHERE word = :word)"
    valid_word = await db.fetch_val(
        query,
        values={"word": guess},
    )

    # 0 if not in table, 1 if in table
    if valid_word == 0:
        abort(400, "Guess is not a valid word.")

    # fetch a tuple of (secret_word, remaining_guesses) from db
    query = """SELECT secret_word, remaining_guesses
        FROM games INNER JOIN game_states ON games.game_id = game_states.game_id
        WHERE games.game_id = :game_id
    """
    info = await db.fetch_one(
        query,
        {"game_id": game_id},
    )
    app.logger.info(query)

    if not info:
        abort(404, "Game with that id does not exist.")

    # check if there are any remaining_guesses left
    if info[1] > 0:
        # returns a tuple of formatted strings (correct_spots, incorrect_spots)
        # ex: ("?a???", "???b?") -> a is correct spot, b is incorrect spot
        state_fields = await _check_string(guess, info[0])

        # initialize game_state info
        game_info = {
            "game_id": game_id,
            "remaining_guesses": info[1] - 1,
            "status": "In Progress",
        }

        # insert into game_history
        await db.execute(
            """
            INSERT INTO game_history(game_id, guess, remaining_guesses)
            VALUES(:game_id, :guess, :remaining_guesses)
            """,
            values={
                "game_id": game_id,
                "guess": guess,
                "remaining_guesses": info[1] - 1,
            },
        )

        # check if the guess was correct
        if guess == info[0]:
            game_info["status"] = "won"
        else:
            if game_info["remaining_guesses"] == 0:
                game_info["status"] = "lost"

        # update the game_states table
        await db.execute(
            """
            UPDATE game_states
            SET status = :status, remaining_guesses = :remaining_guesses
            WHERE game_id = :game_id
            """,
            values=game_info,
        )

        # insert game_state info into response (correct_spots, incorrect_spots)
        game_info["correct_spots"] = state_fields[0]
        game_info["incorrect_spots"] = state_fields[1]
        game_info["guess"] = guess
    else:
        abort(400, "No guesses left.")

    return game_info, 200


# -----------------------------------Listing in progress games------------------------#
@app.route("/users/<string:username>", methods=["GET"])
async def get_progress_game(username):
    """Retrieve the list of games in progress for a user with a given username."""
    db = await _get_db()

    if request.authorization.username != username:
        abort(401, "You cannot this user's games.")

    query = """
        SELECT games.game_id, username, remaining_guesses
        FROM games LEFT JOIN game_states ON games.game_id = game_states.game_id 
        WHERE username = :username AND game_states.status = 'In Progress'
        """
    progress_game = await db.fetch_all(
        query,
        values={"username": username},
    )
    print("Progress of game1:", progress_game)
    if progress_game:
        print("Progress of game:", progress_game)
        return list(map(dict, progress_game))
    else:
        abort(404, "No games in progress for that user.")
