#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
import random
import time

import socketio

NUMBER_OF_PLAYERS = 20
GAME_PIN = 35490014
quiz = [None]


def __main__():
    arr_of_sio_instances = []
    for i in range(NUMBER_OF_PLAYERS):
        arr_of_sio_instances.append(socketio.Client())

    def joined_game(data):
        print("JOINED!!!!")
        print(data)
        quiz[0] = json.loads(data)
        print(type(quiz[0]))

    def set_question_number(data):
        for i in arr_of_sio_instances:
            # print(int(data))
            # print("hi!", data)
            random_num = random.randint(0, len(quiz[0]["questions"][int(data)]["answers"]) - 1)
            print(random_num)
            i.emit(
                "submit_answer",
                {
                    "question_index": int(data),
                    "answer": quiz[0]["questions"][int(data)]["answers"][random_num]["answer"],
                },
            )
            print(i.sid)
            time.sleep(0.1)
        print("Everyone answered!")

    for i in arr_of_sio_instances:
        i.connect("http://localhost:8080/socket.io/")

    arr_of_sio_instances[3].on("joined_game", joined_game)
    arr_of_sio_instances[3].on("set_question_number", set_question_number)
    for i in arr_of_sio_instances:
        i.emit("join_game", {"username": random.randint(0, 30), "game_pin": GAME_PIN, "captcha": None})
        time.sleep(0.1)
    print("Everyone joined!")


if __name__ == "__main__":
    try:
        __main__()
    except KeyboardInterrupt:
        exit(1)
