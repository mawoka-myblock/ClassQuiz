# Socket.IO-Client-Docs

## Init

Event: `join_game`

body: `{game_id}` (obtained by `/api/v1/quiz/join`)

return: `None`

## Get Game Data

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