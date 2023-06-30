<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

# Socket.IO-Client-Docs

## Main structure

### Admin

1. The admin emits the `register_as_admin`-event with the `game_pin` and `game_id`
2. Then he should receive the `registered_as_admin`-event and is successfully registered as an admin, but he could also
   receive the self-explaining `already_registered_as_admin`, which means, that an admin already exists.
   The `registered_as_admin`-event contains the quiz.
3. If players join, the `player_joined`-event will be emitted with the username of the user who joined
4. The admin can now set the index of the question which sould be show on the player-screen with
   the `set_question_number`-event.
5. Now, the admin can emit the `get_question_results`-event to show the results of the question-index which is sent with
   this event, on the screen of the users and on its own.
6. The response of the `get_question_results`-event is the `question_results`-event, containing the results.

> Note: Most of these events require some kind of data.

### Player
TODO
## API-Docs

### Init

Event: `join_game`

body: `{game_id}` (obtained by `/api/v1/quiz/join`)

return: `None`

### Get Game Data

Event: `get_game_data`

body: `{game_id}`

return (example):

```json
{
  "quiz_id": "26058ee8-6c6f-41e0-9d3d-70c82e38d9de",
  "questions": [
    {
      "question": "Is ClassQuiz cool?",
      "answers": [
        {
          "right": true,
          "answer": "Yes"
        },
        {
          "right": false,
          "answer": "No"
        }
      ]
    },
    {
      "question": "Do you like open source?",
      "answers": [
        {
          "right": true,
          "answer": "Yes"
        },
        {
          "right": false,
          "answer": "No"
        },
        {
          "right": false,
          "answer": "Maybe"
        }
      ]
    }
  ],
  "game_id": "d2923b0a-f02e-45b7-8876-268b473beb06",
  "game_pin": "45823169",
  "started": false
}
```
