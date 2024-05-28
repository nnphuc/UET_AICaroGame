from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify, make_response
# from flask_socketio import SocketIO
import json
import time
from Board import BoardGame
import copy
import utils
from threading import Thread
from typing import List

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

import logging

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
# socketio = SocketIO(app, cors_allowed_origins="*")

app.logger.setLevel(logging.ERROR)


def log(*args):
    params = []
    for x in args:
        params.append(f"{x}")

    app.logger.error(" ".join(params))


# Global variance
PORT = 80
team1_role = "x"
team2_role = "o"
size = 15
#################

rooms = {}
room_by_teams = {}

BOARD = []
for i in range(size):
    BOARD.append([])
    for j in range(size):
        BOARD[i].append(' ')

MAX_TIME_BY_BOARD_SIZE = {
    5: 30,
    6: 200,
    7: 300,
    8: 600,  # unchanged
    9: 660,  # 600 + 60
    10: 720,  # 660 + 60
    11: 780,  # 720 + 60
    12: 840,  # 780 + 60
    13: 900,  # 840 + 60
    14: 960,  # 900 + 60
    15: 1020,  # 960 + 60
    16: 1080,  # 1020 + 60
    17: 1140,  # 1080 + 60
    18: 1200,  # 1140 + 60
    19: 1260,  # 1200 + 60
    20: 1320,  # 1260 + 60
    21: 1380,  # 1320 + 60
    22: 1440,  # 1380 + 60
    23: 1500,  # 1440 + 60 (capped at 1500)
    24: 1500,  # capped at 1500
    25: 1500,  # capped at 1500
    26: 1500,  # capped at 1500
    27: 1500,  # capped at 1500
    28: 1500,  # capped at 1500
    29: 1500,  # capped at 1500
    30: 1500,  # capped at 1500
    31: 1500,  # capped at 1500
    32: 1500,  # capped at 1500
    33: 1500,  # capped at 1500
    34: 1500,  # capped at 1500
    35: 1500,  # capped at 1500
    36: 1500,  # capped at 1500
    37: 1500,  # capped at 1500
    38: 1500,  # capped at 1500
    39: 1500,  # capped at 1500
    40: 1500  # capped at 1500
}


def update_time(rooms: List[BoardGame]):
    log_time = time.time()
    while True:
        time.sleep(0.1)
        if time.time() - log_time > 5:
            log_time = time.time()
            log("total rooms: ", len(rooms))
        for room_id in rooms:
            room = rooms[room_id]
            if room.start_game and room.game_info["status"] == None:
                team1_id_full = room.game_info["team1_id"]
                team2_id_full = room.game_info["team2_id"]
                now = time.time()
                if room.game_info["turn"] == team1_id_full:
                    # update time for team1
                    if room.game_info["time1"] >= MAX_TIME_BY_BOARD_SIZE[room.game_info["size"]]:
                        room.game_info["status"] = "Team 1 out of time"
                        room.game_info["score2"] = 1
                        room.game_info["score1"] = 0
                        room.game_info["turn"] = room.game_info["team2_id"]
                    else:
                        room.game_info["time1"] += now - room.timestamps[0]
                else:
                    # update time for team2
                    if room.game_info["time2"] >= MAX_TIME_BY_BOARD_SIZE[room.game_info["size"]]:
                        room.game_info["status"] = "Team 2 out of time"
                        room.game_info["score1"] = 1
                        room.game_info["score2"] = 0
                        room.game_info["turn"] = room.game_info["team1_id"]
                    else:
                        room.game_info["time2"] += now - room.timestamps[1]

                room.timestamps = [now, now]


thread = Thread(target=update_time, args=(rooms,))
thread.start()


@app.route('/init', methods=['POST'])
@cross_origin()
def get_data():
    log("/init")
    data = request.data
    info = json.loads(data.decode('utf-8'))
    log(info)
    global rooms
    global room_by_teams
    room_id = info["room_id"]
    is_init = False
    if room_id not in rooms:
        match_id = 1
        team1_id = info["team1_id"]
        team2_id = info["team2_id"]
        team1_id_full = team1_id + "+" + team1_role
        team2_id_full = team2_id + "+" + team2_role
        room_by_teams[team1_id] = room_id
        room_by_teams[team2_id] = room_id
        board_game = BoardGame(size, BOARD, room_id, match_id, team1_id_full, team2_id_full)
        rooms[room_id] = board_game
        is_init = True

    board_game = rooms[room_id]
    return {
        "room_id": board_game.game_info["room_id"],
        "match_id": board_game.game_info["match_id"],
        "team1_id": board_game.game_info["team1_id"],
        "team2_id": board_game.game_info["team2_id"],
        "size": board_game.game_info["size"],
        "init": True,
    }


@app.route('/', methods=['POST'])
@cross_origin()
def render_board():
    data = request.data
    info = json.loads(data.decode('utf-8'))
    log(info['team_id'])
    global rooms
    room_id = info["room_id"]
    board_game = rooms[room_id]
    team1_id_full = board_game.game_info["team1_id"]
    team2_id_full = board_game.game_info["team2_id"]
    time_list = board_game.timestamps

    if (info["team_id"] == team1_id_full and not board_game.start_game):
        time_list[0] = time.time()
        board_game.start_game = True
    # log(f'Board: {board_game.game_info["board"]}')
    response = make_response(jsonify(board_game.game_info))
    return board_game.game_info


@app.route('/')
@cross_origin()
def fe_render_board():
    global rooms
    if "room_id" not in request.args:
        return {
            "code": 1,
            "error": "missing room_id"
        }
    room_id = request.args.get('room_id')
    if room_id not in rooms:
        return {
            "code": 1,
            "error": f"not found room: {room_id}"
        }
    board_game = rooms[room_id]
    # log(board_game.game_info)
    response = make_response(jsonify(board_game.game_info))
    # log(board_game.game_info)
    return response


@app.route('/move', methods=['POST'])
@cross_origin()
def handle_move():
    log("handle_move")
    data = request.data

    data = json.loads(data.decode('utf-8'))
    global rooms
    room_id = data["room_id"]
    if room_id not in rooms:
        return {
            "code": 1,
            "error": "Room not found"
        }
    board_game = rooms[room_id]
    team1_id_full = board_game.game_info["team1_id"]
    team2_id_full = board_game.game_info["team2_id"]
    time_list = board_game.timestamps

    log(f"game info: {board_game.game_info}")
    if data["turn"] == board_game.game_info["turn"] and data["status"] == None:
        board_game.game_info.update(data)
        now = time.time()
        if data["turn"] == team1_id_full:
            board_game.game_info["time1"] += now - time_list[0]
            board_game.game_info["turn"] = team2_id_full
            time_list[1] = now
        else:
            board_game.game_info["time2"] += now - time_list[1]
            board_game.game_info["turn"] = team1_id_full
            time_list[0] = now
    log("Team 1 time: ", board_game.game_info["time1"])
    log("Team 2 time: ", board_game.game_info["time2"])
    if data["status"] == None:
        log("Checking status...")
        board_game.check_status(data["board"])
    # log("After check status: ",board_game.game_info)

    # board_game.convert_board(board_game.game_info["board"])

    return {
        "code": 0,
        "error": "",
        "status": board_game.game_info["status"],
        "size": board_game.game_info["size"],
        "turn": board_game.game_info["turn"],
        "time1": board_game.game_info["time1"],
        "time2": board_game.game_info["time2"],
        "score1": board_game.game_info["score1"],
        "score2": board_game.game_info["score2"],
        "board": board_game.game_info["board"],
        "room_id": board_game.game_info["room_id"],
        "match_id": board_game.game_info["match_id"]
    }


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=PORT)
