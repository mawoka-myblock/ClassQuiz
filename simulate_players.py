# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0
import random
import time
import sys

import socketio

NUMBER_OF_PLAYERS = 200
GAME_PIN = sys.argv[1]
q_index = 0


def __main__():
    arr_of_sio_instances = []
    for i in range(NUMBER_OF_PLAYERS):
        arr_of_sio_instances.append(socketio.Client())

    def joined_game(data):
        print("JOINED!!!!")

    def time_sync(data):
        print("time sync")
        for i in arr_of_sio_instances:
            i.emit("echo_time_sync", data)
            time.sleep(0.04)

    def set_question_number(data):
        print(data)
        global q_index

        for i in arr_of_sio_instances:
            # print(int(data))
            # print("hi!", data)
            random_num = random.randint(0, len(data["question"]["answers"]) - 1)
            print(random_num, q_index)
            i.emit(
                "submit_answer",
                {
                    "question_index": q_index,
                    "answer": data["question"]["answers"][random_num]["answer"],
                },
            )
            print(i.sid)
            time.sleep(0.03)
        q_index = +1
        print("Everyone answered!")

    for i in arr_of_sio_instances:
        i.connect("http://localhost:8080/socket.io/")

    arr_of_sio_instances[3].on("joined_game", joined_game)
    arr_of_sio_instances[3].on("set_question_number", set_question_number)
    arr_of_sio_instances[3].on("time_sync", time_sync)
    for index, i in enumerate(arr_of_sio_instances):
        i.emit("join_game", {"username": str(index), "game_pin": GAME_PIN, "captcha": None})
        time.sleep(0.03)
    print("Everyone joined!")


if __name__ == "__main__":
    try:
        __main__()
    except KeyboardInterrupt:
        sys.exit(1)
