# End-to-end test findings

Found by the local e2e suite (`bash e2e/run.sh`, see [Running it](#running-it)) on
2026-09-18. **Every H, M and L item below was fixed the same day.** See [How each was
fixed](#how-each-was-fixed). The tables are kept as the record of what was wrong. Each
bug a test could reach was first written as a `test.fail(...)`. Those markers are gone
now, and the same tests stand as regression guards. The UX list and "Worth a look" are
still open.

Convention for new findings: write the test for the behaviour you want, wrapped in
`test.fail(true, reason)`. The run stays green while the bug exists, and the test turns
red ("expected to fail, but passed") once somebody fixes it. That is the signal to
delete the marker.

## How each was fixed

| # | Fix |
|---|-----|
| H1 | `record_answer_once` in `socket_server/helpers.py` appends in a Redis `WATCH`/`MULTI` transaction and runs the duplicate check inside it. It's Redis-side rather than an in-process lock, because production can run several gunicorn workers. 50 simultaneous answers: 50 of 50 stored. The box-controller path uses it too. |
| H2 | `rejoin_game` saves the session and enters the room before it emits `time_sync`, and `submit_answer` reads `ping` with a default. |
| H3 | When the final results arrive, the host podium rebuilds its totals from them (`lib/play/admin/totals.ts`, unit-tested). The per-question tally timer is cancelled on unmount, so it can't add a question twice. |
| H4 | `register_as_remote` requires the game's `game_id` (the host credential), not just the PIN. |
| H5 | `GET /quiz/join/{pin}` now answers 410. `register_as_admin` checks the `game_id` against the stored game. Found while fixing: `PlayGame.to_player_data` was also sending the `game_id` to every player. It's excluded now. |
| H6 | `GET /quiz/get/{id}` accepts `X-Anon-Secret`, and `/edit` sends it. The page shows a message for any status other than 200 instead of rendering blank. After saving, an anonymous quiz returns to its view page. |
| M1 | `QuizInput` rejects a non-numeric timer, or one outside 1–999 s (the editor's own range). |
| M2 | `submit_answer` refuses an answer if its question isn't showing, or if it arrives after the timer plus 1.5 s of grace. The score is clamped to 0–1000. |
| M3 | `kick_player` deletes the player's sid key, so `rejoin_game` refuses them. The player's cookie is cleared as well. |
| M4 | `player_answer` goes to `admin:{pin}`, `everyone_answered` goes to the game room, and `results_saved_successfully` and `session_id` go only to their own socket. |
| M5 | The answers validator refuses an empty list before reading `v[0]`. |
| M6 | `QuizInput` requires at least one question, and `quiz/start` returns 400 for a quiz with none. |
| M7 | Superseded by drafts (MVP.md D14, 2026-09-29): Save keeps an unfinished quiz as a draft and the header says how many questions are left; the server refuses to **start** it (`frogquiz/helpers/completeness.py`). Pinned by `editor` › no correct answer cannot reach the view page, and `api-edge` › no correct answer saves as a draft. |
| M8 | Start, delete and get look at the account and the anonymous secret independently, through `_find_own_quiz`. |
| M9 | The register page reads `returnTo` and passes it on to its "Log in" link. |
| M10 | Back goes to `/my-quizzes` for someone without an account. |
| M11 | The `joined_game` cookie is rewritten on `rejoined_game` with the new socket id. |
| M12 | `join_game` claims the nickname with `SET NX`. |
| L1 | `rejoin_game` resends the current question if one is showing. |
| L2 | The end-screen line checks `username in data`, so a score of 0 still shows. |
| L3 | The podium uses `words.point` with a count. |
| L4 | **Capped at 10, not 4.** The editor stops at 4, but Kahoot imports carry 6, and 10 is the most the CHECK format can express unambiguously. The api-edge test pins 6 as accepted and 11 as refused. |
| L5 | The cookie now lasts 5 hours, matching the game's lifetime in Redis. |
| L6 | The rejoin path fetches game info with the PIN from the cookie. |

Also fixed along the way:
- The host screen said "1 Answers submitted"; the key is now pluralised.
- The lobby said "1 player are waiting".
- **The login page followed any `returnTo`**, including `https://elsewhere`, which is an open redirect right after a password prompt. `safeReturnTo` (unit-tested) now only allows paths on this site.

Found, not fixed:
- ~~`join_game` calls `check_captcha(...)` without `await`~~ — **fixed 2026-10-01**, and it
  was worse than filed. The `await` was added earlier; the remaining bug was that every
  `settings.hcaptcha_key` read inside `check_captcha` was on config.py's *uncalled*
  `lru_cache` wrapper, so it raised `AttributeError` out of `join_game` rather than
  passing anyone. It now fails closed with a logged reason when no provider key is set,
  and `captcha_enabled` (which defaulted to **True** on `/quiz/start`) defaults off and
  is refused outright without a key — so a game demanding an uncheckable captcha cannot
  be opened.
- The editor's yup schema caps a quiz at 50 questions, but its message says 32. The server has no cap (500 questions tested fine).
- **Host events race on the stored game** (found 2026-09-29 writing the exit tests). python-socketio runs each event in its own task, and `start_game`, `set_question_number` and `get_question_results` all read `game:{pin}`, change one field and write the whole thing back. Sent back to back, `set_question_number` can read the game before `start_game` has saved it and then write `started=False` back over it. The host UI can't do this -- it offers "next" only after the server's `start_game` arrives -- so it is a protocol-level gap, not a live bug. A crafted or scripted host could hit it. The fix is per-field storage (`HSET`) or a `WATCH` transaction like `record_answer_once`.

  **This paragraph used to end "the socket specs wait for `start_game` before showing a question for this reason". They did not** -- all ten `start_game` emits in `live-socket.e2e.ts` were fire-and-forget. That is what made *an answer after the host showed the results is refused* flaky: when `current_question` is the field lost to the race, `submit_answer` sees the wrong index, answers `question_not_active` and never emits `player_answer`, so the test failed on its **first** assertion. Measured 2 failures in 10 runs in isolation, which also disproves the earlier note that it only failed under full-suite load. `startGame()` in `e2e/sockets.ts` now waits for the echo, and the test passes 12/12. The server-side race is still there and still worth the `WATCH` transaction; the specs simply no longer provoke it. (Checked whether the new `disconnect` handler contributed: 8/10 with it, 9/10 without -- a one-run difference at n=10, i.e. noise, and it failed with the handler disabled too.)

  **Two specs outside `live-socket.e2e.ts` were still fire-and-forget** and that sweep did
  not reach them: `editor.e2e.ts:103` and `account.e2e.ts:169`. Both `await startGame(host)`
  now. `live-socket.e2e.ts:217` keeps its raw emit deliberately -- there an *attacker*
  emits `start_game` and the test asserts nothing happens.

  **A second failure of *build a quiz by hand, save it, and play it*, 2026-10-02, is
  unexplained.** It failed once in a full-suite run (118/119) with
  `TypeError: Cannot read properties of undefined (reading 'find')`, i.e. `final_results`
  came back with no key for question `0`. That looks exactly like this race, so it was
  attributed to it -- wrongly: measured afterwards, the **unfixed** spec passed 10 out of
  10 in isolation. So the `startGame` conversion above is a correctness tidy-up, not a
  proven fix for that failure, and the cause is still open. Note this is the opposite
  profile to the flake above, which failed 2 in 10 *in isolation*; do not assume the two
  share a cause just because they share a symptom.

  What made it hard to read is a harness defect worth knowing about: `next()` resolves a
  falsy payload to `{}` rather than `null`, so `finalResults`' own
  `expect(r).not.toBeNull()` passes on an empty result and the real failure surfaces one
  line later as an opaque `TypeError`. The spec now asserts which question keys came back,
  and prints the payload, before indexing it.

Severity is for an internal quiz tool used live in a room: **High** means a real game
gives wrong scores, loses answers, or can be taken over by a player. **Medium** breaks
a flow that has an obvious workaround. **Low** is cosmetic or an edge nobody will hit
by accident.

## High

| # | Bug | Where | Test |
|---|-----|-------|------|
| H1 | **Answers are lost when players answer at the same time.** `set_answer` reads the answer list, appends, and writes it back with no lock, so concurrent answers overwrite each other. 50 players answering at once: 1–2 answers stored. Spread over 2 s: 41–44 of 50. Point totals survive (`HINCRBY` is atomic), but the per-question results, the host's podium (H3), "everyone answered" and the already-answered check all read the list. That last one means a player whose answer was lost can answer again. | `frogquiz/socket_server/__init__.py` `set_answer` | `live-socket` › fifty players… |
| H2 | **A player who reloads can never score again.** `rejoin_game` emits `time_sync` before it saves the new session, so the echo fails ("session not available") and no latency is stored. Every later `submit_answer` raises `KeyError('ping')` and is dropped, while the player's screen shows the answer as sent. | `socket_server/__init__.py:127` vs `:144`, `:346` | `game-reload` › reloads in the lobby… |
| H3 | **The projector podium can show wrong scores.** The host screen adds scores up itself in `results.svelte`, 1 s after the results screen mounts. Advancing sooner, or skipping "Show results", drops that question from the projector. Players' own screens use the server totals and are right. | `frontend/src/lib/play/admin/results.svelte:60-81` | `anon-game` › host podium keeps points… |
| H4 | **Any player can become the host with `register_as_remote`.** It checks nothing but the PIN, which every player has. It sends the full quiz, correct answers included, and sets `admin=True` on the player's session, so they can start the game, change questions, kick people and reveal solutions. | `socket_server/__init__.py` `register_as_remote` | `live-socket` › register_as_remote |
| H5 | **Any player can take the host seat via `/quiz/join/{pin}`.** That deprecated, unauthenticated endpoint returns the `game_id`, and `register_as_admin` gives the game to any socket that presents it (the reconnect path cannot tell the host from a player). | `frogquiz/routers/quiz.py` `get_game_id`, `register_as_admin` | `live-socket` › take the host seat… |
| H6 | **Anonymous quizzes cannot be edited.** `/edit` loads through `GET /api/v1/quiz/get/{id}`, which needs a login and ignores `X-Anon-Secret`, so the request gets a 401. The page only handles 200 and 404, so a 401 renders a **blank screen**. The route's own comment says anonymous editing works. | `frontend/src/routes/edit/+page.svelte:41-58`, `quiz.py:38` | `editor` › reopened, edited and saved |

## Medium

| # | Bug | Where | Test |
|---|-----|-------|------|
| M1 | **A non-numeric timer breaks scoring.** Nothing validates `time`: `"abc"`, `"-5"`, `"0"`, `""` and `"99999"` all save through the API. During a game, `int(float("abc"))` raises inside `submit_answer`, so correct answers to that question score nothing. (The editor's own timer field does hold up: 0 and −5 are not saved through the UI.) | `db/models.py` `QuizQuestion.time`, `socket_server/__init__.py:353` | `api-edge` › timer "…" is rejected |
| M2 | **A late answer is accepted and can score negative.** `submit_answer` checks only the question index. It checks neither the timer nor whether results are already showing, so a player can answer after the results broadcast (which reveals the answers). Past the timer, `calculate_score` goes negative and is subtracted from the player's total. Measured: a correct answer 2 s after a 2 s timer ended scored −988. | `socket_server/__init__.py` `submit_answer` | `live-socket` › after the timer…, after the host showed the results |
| M3 | **A kicked player can come straight back.** `kick_player` leaves `game_session:{pin}:players:{name}` in place, which is exactly what `rejoin_game` checks. | `socket_server/__init__.py` `kick_player` | `live-socket` › kicked player… |
| M4 | **Game events reach every game.** `player_answer`, `everyone_answered` and `results_saved_successfully` are emitted with no `room`. One host's "everyone answered" can end another game's question, and one host saving results flips every other signed-in host's Save button to "saved". `connect` also broadcasts each new `session_id` to everyone. | `socket_server/__init__.py:373, 378, 503, 512` | `live-socket` › another game's host |
| M5 | **A question with no answers returns a 500.** The answers validator reads `v[0]` before checking the list is non-empty (`IndexError`). | `db/models.py` `QuizQuestion` validator | `api-edge` › no answers |
| M6 | **An empty quiz can be saved and started.** It opens a live game with nothing in it. | `routers/editor.py` finish, `quiz.py` start | `api-edge` › no questions |
| M7 | **The editor lets you save a question with no correct answer.** Save is gated on the yup schema only (`disabled={schemaInvalid}`), which doesn't require one. The rail marks the question incomplete, but the header warning sits inside the same `schemaInvalid` branch and never shows. | `frontend/src/lib/editor.svelte:214` | `editor` › no correct answer blocks Save |
| M8 | **Signing in locks you out of your own anonymous quiz.** `quiz/start` and `quiz/delete` only look at the anonymous secret when there is no session. Sign in without claiming first, and your own quiz 404s on both. | `quiz.py` `start_quiz`, `delete_quiz` | `account` › signing in does not lock you out… |
| M9 | **"Keep this quiz" sign-up doesn't bring you back.** The view page links to `/account/register?returnTo=/view/{id}`. The register page never reads `returnTo`, and its "Log in" link doesn't pass it on, so the new account has no route back to the quiz to claim it. | `frontend/src/routes/account/register/+page.svelte` | `account` › brings you back to the quiz |
| M10 | **The editor's Back link sends an anonymous user to a login wall.** It is hard-coded to `/dashboard`. This overlaps with backlog item 6 (merging `/my-quizzes` into `/dashboard`), which would fix it. | `frontend/src/lib/editor.svelte:177` | `editor` › Back link |
| M11 | **A second reload drops the player.** The `joined_game` cookie is written on join only. `rejoin_game` moves the server's record to the new socket id, so the cookie keeps the old one and the next reload is refused silently. | `frontend/src/routes/play/+page.svelte:100-111` | `game-reload` › reload twice |
| M12 | **Two players can join with the same nickname at the same moment.** The nickname check is check-then-set with no `SET NX`. 5 simultaneous joins as the same name: all 5 got in, and their scores merge into one hash field. | `socket_server/__init__.py` `join_game` | `live-socket` › racing for the same nickname |

## Low

| # | Bug | Where | Test |
|---|-----|-------|------|
| L1 | A player who reloads during a question doesn't get it back; they wait for the next one. `rejoin_game` sends the game, not the current question. | `rejoin_game` | `game-reload` › gets the question back |
| L2 | A player on 0 points gets no "Your score / place" line at the end (`{#if data[username]}`, and 0 is falsy). | `lib/play/admin/final_results.svelte:134` | `anon-game` › zero points |
| L3 | The podium shows the raw text `words.point_plural`; en.json has `point_one` / `point_other`. It also overflows at 390 px. | `final_results.svelte:94` | `anon-game` › raw translation key |
| L4 | More than 4 answers per question are accepted through the API. For a multiple-answer question with 10+ options, the scoring format (concatenated indices) becomes ambiguous: ticking options 1 and 2 sends `"12"`, the same as ticking option 12. | `QuizQuestion`, `helpers.check_check_question` | `api-edge` › more than four answers |
| L5 | The `joined_game` cookie is set with `expires: 3600`, which js-cookie reads as **days** (about 10 years), not seconds. | `play/+page.svelte:102` | — |
| L6 | After a rejoin, `/play` fetches `check_captcha/` with an empty PIN (it uses the page's `game_pin`, which is blank after a reload), so `game_mode` is unset. | `play/+page.svelte:94` | — |

## UX and polish (no test; noted while driving the UI)

- **Nicknames need at least 4 characters, and nothing says so.** The button just stays disabled, which blocks common names like "Ana" or "Rui". The server itself allows anything non-blank up to 50 characters.
- **Digits typed into the PIN box before the page hydrates are lost.** The PIN form also has no submit handler, so Enter or a native submit reloads the page. The theme toggle has the same pre-hydration gap: a click in the first moment after load does nothing. On a slow phone that first moment is noticeable.
- **The view page's Play button has no accessible name.** This is already covered by backlog #17.
- **The editor rail's description box has no label or placeholder.** When it is required and empty, it's an unexplained red box.
- **Download is disabled for an anonymous owner**, with no explanation why.
- **The dashboard hint says "Press Ctr+k"** instead of "Ctrl+k".
- **The navbar has no current-page indicator.** The permanently highlighted Play pill reads as "you are here" on every page.
- **Saving lands in different places:** an edit returns to `/dashboard`, while a new quiz goes to its view page.
- **The navbar and footer still show Docs and GitHub links.** The feature triage in CLAUDE.md lists these as hide candidates.

## Worth a look, not bugs as such

- `GET /api/v1/utils/ip-lookup/{ip}` forwards the IP to `ip-api.com` over plain HTTP. It needs a login, and it isn't upstream infrastructure, but it is a third-party data flow of the kind CLAUDE.md asks to keep an eye on.
- `/api/v1/internal/testing/user/{email}` is registered in every environment. It is gated on `SECRET_KEY`, but:
  - the key arrives as a query parameter, so it ends up in access logs;
  - the comparison isn't constant-time;
  - it returns the full user row, password hash included.
- **CLAUDE.md's verification snippet is out of date.** It checks `getComputedStyle(document.body).backgroundColor`, but `app.css` deliberately keeps `body` transparent and puts the page ground on `html`. The check should read `document.documentElement`.

## What held up

These were tested and passed. They're worth knowing before anyone "fixes" them.

- **Large quizzes:** 200- and 500-question quizzes save, read back complete and start in under a second each. Text of 5,000 characters is stored intact.
- **Anonymous ownership:**
  - A wrong or missing secret gets the same 404 as a quiz that doesn't exist, on start, edit and delete.
  - An anonymous quiz can't be made public.
  - The ownership hash is not exposed through the public endpoint.
  - Claiming works, and claiming twice returns 404.
  - Once a quiz is claimed, its old secret no longer works.
- **Joining:**
  - A wrong PIN is refused.
  - A duplicate nickname is refused, including one with extra spaces around it.
  - Over 50 characters, or blank, is refused.
  - Emoji, accents and Arabic script are accepted.
  - Nobody can join after the game has started.
  - A second answer to the same question, or an answer to a question that isn't showing, is refused.
- **Multiple-answer questions** score the exact set only, as documented.
- **Accounts:**
  - Registering and logging in (two-step) work.
  - A wrong password gets a clear message.
  - The dashboard lists only your own quizzes.
  - Someone else's private quiz can't be started.
  - A signed-in owner can edit and save.
  - Saved results appear on `/results`.
- **Explore:** a public quiz is found by search; a private one never is.
- **The host can reload mid-game** and carry on.
- **Layout:** there's no horizontal scroll on any public or signed-in page at 390, 834 or 1440 px. The theme toggle switches both the class and the background, and survives a reload.

## Running it

```sh
bash e2e/run.sh                          # whole suite, about 15 minutes
bash e2e/run.sh e2e/live-socket.e2e.ts   # one spec
KEEP_UP=1 bash e2e/run.sh --list         # bring the stack up and leave it running
bash e2e/stop.sh                         # stop a stack left up with KEEP_UP=1
```

**The API does not reload.** `run.sh` starts uvicorn without `--reload`, so a stack left
up with `KEEP_UP=1` keeps serving the Python it started with. Edit anything under
`frogquiz/` and the browser still talks to the old code — Vite hot-reloads the frontend,
which makes it look like the change landed. This cost three rounds of "the fix didn't
work" on the anonymous image upload: `storage.py` had been fixed, the process was two
hours old, and every upload was still answering 401. Restart the API (or the stack)
after a backend edit, and when a fix appears to do nothing, check the process start time
against the file mtime before touching the code again.

It needs nothing beyond what the repo already needs: the pipenv venv, pnpm, the
installed Postgres binaries (a throwaway cluster is created on port 5433) and Edge.
fakeredis is pip-installed into the venv, and a portable Meilisearch exe is downloaded
once into `e2e/.tools`. Logs, the HTML report, and traces of failed tests go to
`e2e/.data`, which is gitignored.

| Spec | What it covers |
|------|----------------|
| `anon-game` | A full anonymous game with three phone-sized players, driven in real browsers. |
| `api-edge` | Malformed and extreme input straight to the API, plus anonymous ownership. |
| `live-socket` | The socket protocol: a 50-player crowd, joining rules, answering rules, and host control. |
| `editor` | Building a quiz by hand, the Save guard, the timer field, editing, and phone width. |
| `account` | Register, log in, dashboard, claim, Explore, saved results. |
| `game-reload` | Player and host reloads mid-game. |
| `responsive` | The overflow sweep at three widths, and the theme toggle. |
| `disconnect` | A closed tab stops blocking the question; a reload keeps the player on the host's list. |
| `uploads` | The editor's picker: the size rule, an oversized file, a type the server refuses, and a real upload. |
