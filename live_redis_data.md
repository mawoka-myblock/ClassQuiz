<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

## game_session:{GAME_PIN}:players:{PLAYER_NAME} [string]

Contains only the sid (socket.io session-id) of {PLAYER_NAME}

## game_session:{GAME_PIN}:{QUESTION_INDEX} [string]

Stores the answer per question which the players submitted

model: _AnswerDataList

example-data:

```json
[
    {
        "username": "Mawoka",
        "answer": "a",
        "right": false,
        "time_taken": 4994.246999999999,
        "score": 0
    }
]
```

## game:{GAME_PIN} [string]

Stores the data for the game

model: PlayGame

example:

```json
{
    "quiz_id": "be7089c6-ec97-4da9-bb3e-1aa9b67fb939",
    "description": "asddsadas",
    "user_id": "7cbabbc5-fdbb-4d8b-9a89-7005dfdb6f33",
    "title": "Test",
    "questions": [
        {
            "question": "sdadsadas",
            "time": "20",
            "type": "ABCD",
            "answers": [
                {
                    "right": false,
                    "answer": "a",
                    "color": null
                },
                {
                    "right": true,
                    "answer": "b",
                    "color": "null"
                }
            ],
            "image": null
        }
    ],
    "game_id": "7b572f2b-cf7b-47a9-ac0f-446dac22eab0",
    "game_pin": "623490",
    "started": true,
    "captcha_enabled": false,
    "cover_image": null,
    "game_mode": "kahoot",
    "current_question": 0,
    "background_color": null,
    "background_image": null,
    "custom_field": null
}
```

## game_session:{GAME_PIN}:player_scores [hash]

Just stores the score the player has at any point of the game

data:

`{PLAYER_NAME} = {SCORE}`

## game_session:{GAME_PIN} [string]

Mostly unused, only used to check if an admin is registered. The `answers` never change.

model: GameSession

example:

```json
{
    "admin": "qo1yt-rBG4HyX0YGAAAB",
    "game_id": "7b572f2b-cf7b-47a9-ac0f-446dac22eab0",
    "answers": []
}
```

## game_session:{GAME_PIN}:players [set]

A list of all current players, used to get the current number of players to check if everyone has answered

entry:

```json
{
    "username": "Mawoka",
    "sid": "VSprqk7xGKaH5QbwAAAD"
}
```

## game:{GAME_PIN}:current_time [string]

The time when the question was shown to measure the time the players needed to answer

## game_pin:{GAME_ID}:{QUIZ_ID} [string]

**Seems** to be unused

Returns the Game-pin

## game:{GAME_ID}:players:custom_fields [hash] [OPTIONAL]

Holds the custom-field data, but is only set if the custom-field is enabled.


data: `{PLAYER_NAME} = {CUSTOM_FIELD_VALUE}`

## game:cqb:code:{cqc_code} [string]

{cqc_code} is the code used to join with a **C**lass**Q**uiz**C**ontroller

Only holds the game-pin
