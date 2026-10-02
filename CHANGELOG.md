# Changelog

All notable changes made during Claude-assisted work on frogQuiz are logged here, most recent first.

## Unreleased

### `e2e/stop.sh` did not know about the mail sink

Half a change, found the way they always are: the next full suite died on "port 2526 is
already in use" before a single test ran. `run.sh` gained the mail sink on 2 Oct and
`stop.sh`'s port list did not, so a `KEEP_UP=1` stack left it listening and nothing could
start afterwards. Both lists now carry it, with a comment saying to keep them in step.

### The last two join-screen items, and a handover

Both were flagged as taste rather than defect and left for a decision; François called for
them on 2 Oct.

- **The join card no longer floats in the middle of a laptop viewport.** `fq-stage` centres
  on both axes, which is right for the game surfaces a room reads and wrong for a form: at
  1440x900 the card sat with about 40% of the viewport empty above it and read as a page
  that had failed to load. It is biased upward from `sm` and **unchanged on a phone**,
  where it was already right and where every player actually is. Measured: the card's top
  moved from 41% down the viewport to 22% at 1440, and stayed at 41% at 390.
  `fq-stage` itself is untouched, so no game surface moved.
- **A long quiz title no longer swamps the lobby.** It was `text-4xl`/`5xl`, which made it
  the loudest thing on the screen — louder than "You're in, ana", which is what a player
  is actually looking for. "Q4 Security Awareness Refresher" ran to three lines on a phone.
  Now `text-2xl`/`4xl`: measured 36px → 24px, three lines → two. Still the largest element,
  no longer the first one you read.

Both verified in a browser at 390 and 1440, with no horizontal overflow at either.

`HANDOVER.md` is new: the branch for François and Gonçalo, leading with the three things
that have a deadline (the Oracle VM before 31 October, proving mail on the deployed site,
and confirming the `worker` container runs) and linking everything else.

### Everything green, verified at the end

| Suite | Result |
| --- | --- |
| e2e | **127 passed**, 10.0 min |
| Backend | **147 passed**, 1 skipped |
| Unit | **126 passed** |
| `flake8 .` | 0 |
| `eslint .` | 0 errors (108 warnings, all pre-existing) |

Measured after the last change, not carried forward from an earlier run.

The six journeys are the headline, and what they found is the honest part: **every
first-run failure was my own assumption, not a product bug** — nine of them. Wrong copy,
wrong role (link vs button), wrong moment (before a transition settles), wrong encoding
(base64, CRLF, oklch), wrong element type (contenteditable vs input), wrong state (podium
vs lobby). The app was right every time, which is the useful result: a journey encodes
what a *user* expects, and where that disagreed with the app, the app won. The table is in
[`docs/session-2026-10-02.md`](docs/session-2026-10-02.md), and each spec carries a
comment naming the assumption and the truth.

Two e2e failures remain unexplained and are recorded **without** a shared cause being
claimed: `editor.e2e.ts › build a quiz by hand` and `game-reload.e2e.ts › a player can
reload twice`, one occurrence each in five full runs, both passing in isolation (3/3 and
10/10). They share a symptom — the player does not get the question — and that is exactly
the reasoning that produced a retracted attribution earlier in the session.

### User journeys, and a mail relay for the e2e stack

The suite was organised by mechanism — sockets, editor, uploads, exits — and thorough at
it. A journey test fails for a different reason: not "this control is wrong" but "you
cannot get from here to there". Three now exist, each narrated with `test.step` so a
failure names the step:

- **`journey-recovery`** — sign up, forget the password, request a reset, **read the real
  email**, follow the link, set a new one; the old password is refused and the link is
  dead the second time.
- **`journey-first-game`** — land on `/`, Create with no account, write two questions
  (one of them CHECK), save, host, two phones join, play both, podium, Back to My
  Quizzes with the quiz still listed.
- **`journey-teammate`** — owner publishes, a teammate finds it in Discover, cannot read
  which answer is right (D12) or download the sheet (D18), but can run it. D12 and D18
  contradicted each other for a day and were tested in separate files; here they are
  asserted on the same page, as one person meets them.

The unlock is **`e2e/mailsink.py`**: a ~90-line asyncio SMTP server, no new dependency,
writing every message to `e2e/.data/mail/*.eml`. Until now `/forgot-password` answered
503 in e2e because `mail_configured` was false with no relay, so password recovery — a
must-do in `MVP.md` before sharing — could not be tested at all. Hand-rolled rather than
aiosmtpd because the backend sends through plain `smtplib` with no STARTTLS and no AUTH
when the credentials are blank, so EHLO/MAIL/RCPT/DATA/QUIT is the whole surface needed.

That buys the parts that actually break in production: the Jinja templates render, and
the reset link is built from `ROOT_ADDRESS` rather than the API's own host. On a split
Netlify/Oracle deploy those are different hostnames, and getting it wrong sends every
user to a host serving no page. It does **not** prove a real provider accepts the mail;
that stays on the manual checklist in `DEPLOY.md`.

`editor.e2e.ts`'s private UI helpers moved to `helpers.ts`, so a journey builds a quiz
through the editor like a person instead of posting one to the API. `saveButton` became
`saveQuizButton`.

**Every first-run failure was mine, not the product's** — worth recording, because each
looked like a finding:

- **A visitor is meant to see the answers.** D12 hides *which* one is right, not the
  options: a visitor needs to see what a quiz asks to decide whether to play it. The test
  now asserts the `sr-only` "Correct" label is absent for a visitor **and present for the
  owner on the same page**, so it cannot pass by the marker being deleted for everybody.
- **The podium's exit is a link, not a button**; log out is a navbar link to
  `/api/v1/users/logout`, rendered twice (desktop and mobile sheet).
- **The reset email is base64.** `MIMEText(..., 'utf-8')` encodes that way, so a regex
  over the raw `.eml` finds nothing in a message that does contain the link.
- **SMTP is CRLF**, so splitting MIME parts on `\n\n` returned empty bodies.

Two assertions exist because that decoding forced the question: the link must appear in
**both** the plain and HTML parts, and the two must agree. A `multipart/alternative`
whose plain half has no link is broken for anyone reading mail as text, and nothing else
in the suite would notice.

### Every decision in MVP.md §4.0 is now signed

François signed D1 and D3–D15 on 2026-10-02 after asking for each to be explained, having
already answered D2 and D16 with "like Kahoot" and taken D8, D9, D17 and D18. Nothing in
that table is waiting on anybody. D2 and D16 now record what "like Kahoot" turned out to
mean, with the research behind each, rather than just a tick.

### Two fixes on the join screen

Found by shooting `/play` against a live stack rather than reading the markup.

- **The PIN box no longer pre-fills something that looks like a PIN.** `placeholder="000000"`
  in a mono face at `0.35em` tracking is indistinguishable from a typed value — most
  visibly on the error state, which said "No game with that PIN" directly above what
  looked like a PIN. The placeholder is gone and the hint carries the count instead:
  "Enter the 6-digit PIN from the host's screen." Same change on the landing page's PIN
  card, which had the same placeholder.
- **A Submit that is not ready reads as inert rather than broken.** shadcn's
  `disabled:opacity-50` over a near-black primary lands on a flat mid-grey with pale text,
  and that is what a player looks at for the whole time they are typing. It is
  `bg-muted` / `text-muted-foreground` at full opacity now — a pairing `theme-tokens.test.ts`
  already holds to AA in both themes. Scoped to the two join forms and the landing card
  rather than changed on the shared Button, which every surface uses.

`frontend/e2e/join.e2e.ts` covers both, and both were confirmed to fail against the old
markup (`rgb(24,24,27)` for the disabled button, and a placeholder matching `/\d/`).

Two things that test got wrong first, worth knowing before writing another like it:

- **A rejected PIN clears the field**, so a bad PIN is not a route to the enabled button —
  the first version asserted the button stays enabled after an error and failed against
  correct code. It reaches the enabled state through a real game's nickname step instead.
- **`getComputedStyle` returns `oklch(...)` verbatim** for a token defined in oklch, so
  parsing numbers out of that string yields lightness and chroma, not channels. Colours
  are painted to a 1×1 canvas and read back as sRGB. And because the button carries
  `transition-all`, the background has to be polled until it settles: read once, it
  returns a colour partway between the two tokens — the test first failed on
  `rgb(236,236,237)`, which is neither, and looked like an app bug.

### Green, with one failure on record

Two full e2e runs on 2 Oct: **118/119 then 119/119** (8.9 min). Backend 146 passed /
1 skipped, unit 126 passed, `flake8 .` 0, `eslint .` 0 errors. The suite is 119 tests now,
up from 115.

The second run passing does **not** close the first run's failure: that is 1 occurrence in
2 runs of an intermittent fault, not a fix. It stays open in `TODO.md`.

### One e2e failure, cause still unproven

The full suite came back 118 passed / 1 failed:
*editor.e2e.ts > build a quiz by hand, save it, and play it*. I attributed it to the
fire-and-forget `start_game` race fixed earlier this session, then measured it: **the
unfixed spec passed 10 out of 10 runs in isolation**, so that attribution is not
supported and the cause is still unknown. The failure has been seen once, under
full-suite load.

The two `startGame` conversions below are kept anyway — awaiting the server's
acknowledgement is strictly better than not, and it is what every other spec does — but
they are a correctness tidy-up, not a proven fix. `docs/e2e-findings.md` was also still
claiming every spec waits for `start_game`, which was not true.

What the measurement did establish is a harness defect that cost the diagnosis:
`next()` resolves a falsy payload to `{}` instead of `null`, so `finalResults`' own
`expect(r).not.toBeNull()` passes on an empty result and the failure surfaces one line
later as `TypeError: Cannot read properties of undefined (reading 'find')`. The spec now
asserts which question keys came back before indexing them, so a recurrence names the
payload instead of hiding it.

- `host.emit('start_game', {})` returns immediately. When `set_question_number` reaches
  the server first, the question never goes active, both answers are refused, and
  `finalResults` comes back with no rows for question `0` — hence
  `TypeError: Cannot read properties of undefined (reading 'find')` rather than a
  readable assertion failure.
- `editor.e2e.ts:103` (the one that failed) and `account.e2e.ts:169` (same pattern, had
  not lost the race yet) both `await startGame(host)` now.
- `live-socket.e2e.ts:217` keeps its raw emit on purpose: there an **attacker** emits
  `start_game` and the test asserts nothing happens. Converting it would have deleted a
  real security assertion.

Not a flake and not caused by that day's changes: the spec starts its game over the API
and never touches the start modal.

### The host decides what the phone shows (D16)

- The start-game modal has a switch, **"Show questions and answers on players' devices"**,
  off by default. Off, a player sees four coloured shapes and reads the question off the
  host's screen; on, their phone carries the question text, its image and the answer text.
  It is per game and not remembered, so turning it on for a call does not follow you into
  the next room with a projector.
- This is Kahoot's own behaviour: shapes by default, plus a setting of the same name that
  is free on every Kahoot plan. François chose "make it like Kahoot" on 2026-10-02.
- Almost nothing had to be built. Both render paths in `lib/play/question.svelte` already
  existed and worked, and `ReturnQuestion` already put the question text and image on the
  wire — upstream exposed the choice as two game modes picked before the game started and
  labelled "Normal" and "Old-School", which told a host nothing about what they did. The
  modal was simply hardcoding `game_mode: 'kahoot'`. Same wire value, named after its
  effect and moved to where the host is already making decisions.
- `frontend/e2e/player-screen.e2e.ts` (3 tests) drives a real game at phone width and
  asserts on **visible** text, not the accessible name: the answer is the tile's
  `aria-label` in both modes, which is right for a screen reader and is how the other
  specs click answers, so a role-based locator finds the tile in shapes mode too and would
  prove nothing. The third test pins that the switch does not persist between games.

### An upload directory that does not exist is created

- `LocalStorage` never created its `base_path`, and `upload` is a bare `open(..., "wb")` —
  so a `STORAGE_PATH` pointing at a directory that is not there yet meant **every image
  upload answered 500** with a `FileNotFoundError` in the log and nothing in the response
  saying why. Docker masked it, because the bind mount in `docker-compose.yml` creates the
  path; a bare-VM install (the "Deploying to any Linux VM" path in `DEPLOY.md`), a typo, or
  a fresh test box all hit it. I lost a backend-suite run to exactly this.
- Created eagerly in `__init__` and fatal if it cannot be: the class is only built when the
  backend is `local`, the wrapper already raises on bad config at construction, and an app
  that cannot write uploads should say so at startup rather than once per person who adds a
  picture.

### Oracle's Always Free ARM allowance was halved

- `DEPLOY.md` told anyone deploying to create a 4 OCPU / 24 GB `VM.Standard.A1.Flex` and
  called it "the whole Always Free ARM allowance". Oracle now states that allowance as
  **1,500 OCPU hours and 9,000 GB hours a month, or 2 OCPUs and 12 GB** — half what the
  file said, with no announcement. An over-allowance tenancy does not get trimmed to fit:
  every A1 instance in it is disabled and then deleted after 30 days.
- Corrected to 2/12, with a pointer to Oracle's own page rather than asking anyone to
  trust the file, a note that Always Free is home-region-only, and a warning that Oracle
  reclaims idle instances (all three of CPU p95, network and memory under 20% over seven
  days — which a quiz tool used once a week meets). Hetzner's price corrected too: the
  CX22 at "about EUR 4" is now a CX23 at EUR 5.49 plus EUR 0.50 for the IPv4.
- Full analysis, with a dated checklist, is **issue #22**.

### Repo hygiene

- `e2e/.venv/` and `.venv/` are gitignored. `e2e/run.sh` documents `E2E_VENV` for an
  in-tree virtualenv, and nothing stopped `git add -A` from committing a few hundred MB of
  wheels.
- The same two paths are excluded in `.flake8`, so a local `flake8 .` reports what CI's
  does. CI installs outside the tree and never saw them; an in-tree venv added about 64,000
  errors from other people's packages.

### Results are the owner's (D18)

- `GET /api/v1/eximport/excel/{quiz_id}` is scoped to the signed-in user's own quizzes and
  404s (not 403) for anybody else's, so it says nothing about whether the id exists. The
  Download button on the view page is behind `{#if is_owner}`.
- The spreadsheet contains the answer key, and the same page already hid the correct
  answers from a non-owner (`show_answers = is_owner`), so any signed-in teammate could
  read the answers to a quiz they were about to play. François closed it on 2026-10-02.
- Pinned from both sides: `test_excel_export_is_owner_only` on the route, and a new
  `practice.e2e.ts` case asserting the button is absent for a non-owner **and** that the
  endpoint refuses them. The existing download test now saves its quiz through the
  signed-in context, so it owns what it downloads.

### Four lint failures I had shipped

Backend and frontend lint were both red on `main`, from my own earlier commits this
session. CI runs `flake8` (not black) and `eslint`, and both were failing:

- `frogquiz/config.py` — `upload_limits()` had one blank line before it, not two (E302).
- `frogquiz/helpers/__init__.py` — `import re`, left behind when `_QUIZ_IMAGE_KEY_REGEX`
  was deleted.
- `frogquiz/routers/quiz.py` — `storage`, unused since image deletion moved into the
  reference-counting helper.
- `frogquiz/routers/storage.py` — `MAX_UPLOAD_SIZE`, which belongs to the middleware; the
  route checks `UPLOAD_LIMITS` per type.
- `src/routes/admin/+page.svelte` — `export_token` was assigned from the socket and never
  read; the download href uses the payload directly.
- `src/lib/play/admin/results.svelte` — `getLocalization` and its `t`, unused since the
  strings there were replaced.

`flake8 .` is now 0 across the repo and `eslint .` is 0 errors (108 pre-existing warnings
remain, all `{@html}` and unkeyed `{#each}` in untouched files).

### Mail testing has a recipient

- `francois.prevot@hotmail.com`, François's call on 2026-10-02. External and strict about
  SPF/DKIM, which is the point: a relay misconfiguration an internal address would wave
  through gets caught. Steps in `DEPLOY.md` under "Testing it for real".

### Decisions recorded

- **D8** contact address: the `francois.prevot@frog.co` placeholder stands (F, 2 Oct).
- **D9** login architecture: an account is what makes a quiz permanent, no SSO yet (F, 2
  Oct). `frogquiz/oauth/` stays config-gated and unwired.
- **#16, #17 and #19 closed** on François's say-so, each with a comment recording the
  evidence rather than a bare close.

### Upload limits retuned

- Per-file image ceiling is **5 MB**, down from 8 MB (`max_image_upload_size`). All three
  enforcement layers follow it: Caddy's `request_body` cap on `/api/v1/storage/*` is 6 MB
  (framing headroom), and the `Content-Length` guard and the counted-bytes check read the
  setting, so there is still one place the number is written.
- Per-account quota is **1 GiB**, up from 256 MiB (`free_storage_limit`). The old number
  was sized against a free Postgres plan rather than the disk the files sit on.
- The browser's fallback (`FALLBACK_MAX_FILE_SIZE`, used only until
  `GET /api/v1/storage/limits` answers) moved to 5 MB with it. The hint under the picker
  and every test read the server's number, so no copy or assertion was hardcoded.
- `MVP.md` no longer says deleting a quiz leaves its cover and background image behind —
  that was fixed on 1 Oct and the line was stale.

### Everything green

- Full suite verified end to end on 2 Oct: **e2e 115/115 in 8.5 minutes**, backend 146
  passed (1 skipped), unit 126 passed, production build OK. The previous full run was 10
  failed / 105 passed in 29 minutes — the time difference is almost entirely failing tests
  burning their five-minute timeouts.
- All ten of those failures were self-inflicted and are now fixed: six specs broken by the
  Kahoot round sequencing and the podium redesign, one by an Excel permission change that
  was itself reverted, and the socket "flake" that turned out to have a real cause.

### The flaky socket test had a root cause

- *an answer after the host showed the results is refused* was written off as a flake —
  by me, as "passes 3/3 in isolation". Measured properly it fails **2 in 10 in
  isolation**, so that was wrong, and it was failing on its *first* assertion, not the
  one the test is named for.
- Cause: every `start_game` emit in `live-socket.e2e.ts` was fire-and-forget, so
  `set_question_number` could read `game:{pin}` before `start_game` had saved and write
  the whole object back over it. When `current_question` is the field lost,
  `submit_answer` sees the wrong index, answers `question_not_active` and never emits
  `player_answer`. `docs/e2e-findings.md` described this race and claimed the specs
  waited for `start_game` "for this reason" — they did not; that claim is corrected.
- `startGame()` in `e2e/sockets.ts` waits for the echo, and all nine legitimate call
  sites use it. The tenth is left raw on purpose: it is an attacker who should *not* be
  able to start the game, so waiting for an echo would be wrong. **12/12 now**, and the
  whole spec is 21/21.
- The underlying server-side race is untouched and still wants an `HSET` or a `WATCH`
  transaction; the specs just no longer provoke it.
- Also checked whether the new `disconnect` handler contributed: 8/10 with it, 9/10
  without. A one-run difference at n=10 is noise, and it fails with the handler disabled,
  so the flake predates it — but n=10 cannot clear the handler either, which is why the
  numbers are recorded rather than a verdict.

### Deleting an image actually frees the space

- **Deleting a quiz never freed its images, and nor did the 30-day anonymous sweep.** Both
  went through `collect_quiz_image_keys`, whose regex `^.*/(.{36}--.{36})$` only ever
  described upstream's old double-key form. A modern upload stores the bare `StorageItem`
  UUID — no slash, no `--` — so it matched nothing and every image of every deleted quiz
  stayed in storage for good, still charged to its owner's quota. For expired anonymous
  quizzes that is unbounded growth from people who never come back. One shared,
  reference-counted `release_quiz_images` now serves all three paths (quiz delete, the
  sweep, and an image taken off a question), and it covers cover and background images
  too. The old helper is deleted rather than left as a function that silently matches
  nothing.

- **`anon-game.e2e.ts` carried four stale assertions, all from my own changes today**, and
  it is the one spec that drives a whole game, so it was failing for a different reason
  each time I looked. It clicked "Next Question" after "Show results" (the standings step);
  it matched `getByText('1st Place')` unscoped on both the host *and* the player, the
  player side having become ambiguous because `max-sm:sr-only` keeps the podium label in
  the DOM at phone width where `hidden` had removed it; it asserted the winner sees
  "You're on place 1!", which `player-medal.e2e.ts` explicitly asserts they do **not**
  since the medal replaces it — two specs contradicting each other; and it expected the
  export button's old label, "Request result download", which became "Download results"
  when that export became one press. Swept every place-label and button-label assertion in
  every spec this time rather than waiting for them to turn red one at a time.
- **Four more specs were broken by the Kahoot round sequencing, not just `anon-game`.**
  `game-export`, `podium` and `player-medal` all clicked "Get final results" or "Next
  Question" straight after "Show results" and hung on the Scoreboard screen. All three use
  the shared helpers now. `game-reload`'s "whatever screen the host came back on" regex
  also gained `Scoreboard`: it passes today only because the reload lands mid-question, so
  it was one timing change from a confusing failure. Audited every spec that mentions
  "Show results" rather than fixing them as they turned red.
- The host podium says "1st Place" twice by design — once on the gold block, once in the
  standings row for the winner — so `anon-game.e2e.ts`'s bare `getByText('1st Place')` was
  a strict-mode violation rather than a check. Scoped to `.podium-block.is-gold`, with a
  note saying why. This was the last of the breakage from today's podium and
  round-sequencing changes.

- **`storage_used` was only ever incremented.** The `calculate_hash` worker job added each
  upload's size and nothing anywhere subtracted it — not the delete endpoint, not the
  quiz-update job that unlinks a replaced image, not account deletion. The figure was a
  lifetime upload counter rather than usage, so the quota built on it was a lifetime cap:
  swap a cover image enough times and you are locked out for good with nothing to reclaim.
  Harmless while the quota went unenforced — which, as of earlier today, it no longer is,
  so this was a lockout the enforcement created.
- `DELETE /api/v1/storage/meta/{file_id}` now releases the file's bytes, clamped at zero
  because the column declares `minimum=0` and every row predating the size fix stores 0.
- Taking an image off a question used to only unlink the relation, leaving the file in
  storage for good. It now deletes the orphan once nothing points at it and gives back its
  bytes — reference-counted first, because images are many-to-many with quizzes and a
  duplicated quiz shares them. The editor's own X is the whole affordance; still no media
  library.
- Verified end to end on a live stack (4096 bytes billed, deleted, back to 0). It silently
  reported no decrement at all until the API was restarted — `run.sh` starts uvicorn
  without `--reload`, exactly the trap `docs/e2e-findings.md` warns about. Written up in
  `docs/uploads.md` with the commands.

### A game survives someone closing their laptop

- **There was no socket `disconnect` handler at all.** A closed tab stayed in the set
  that "everyone answered" is counted against, so once one person left, the question
  could never end early again and the host sat through every full timer for the rest of
  the game. That is the worst thing that can happen to a game running in a room.
  Disconnecting now drops the player from the count and re-checks whether the question
  can close — deliberately *not* the same as leaving: the rejoin key stays, so a
  backgrounded phone can still come back, which is the whole reason this could not just
  call `leave_game`.
- **A player who reloaded vanished from the host's lobby for good.** The host filters its
  list on `player_left` and only ever adds on `player_joined`, and `rejoin_game` told
  nobody. It does now.
- **A refused answer was silent.** The server emits `question_not_active` when an answer
  arrives after the reveal or past the timer; nothing in the frontend listened. The
  screen locks in the moment a tile is tapped, so a refused answer still read "Answer
  locked in" and the player found out only from a +0 on the results — which looks like a
  bug rather than a wrong answer. It now says "That one did not count".
- Fixed a listener leak next to it: the player's question component is recreated per
  question (`{#key unique}`) and its `everyone_answered` subscription was never released,
  so one copy accumulated per question, each holding a destroyed component's state alive.

### Two things that handed out more than they should

- **The Excel owner filter was reverted.** I had narrowed `GET /eximport/excel/{id}` to
  the quiz's owner, reporting it as a hole in a boundary the UI already drew. That was a
  misreading: the `{#if is_owner}` on the view page guards **Edit**, while Download is
  gated only on `disabled={!logged_in}`. So any signed-in visitor downloading any quiz is
  the advertised behaviour — and CLAUDE.md keeps the search bar precisely for "sharing
  quizzes made by other people on the team". Narrowing it broke `practice.e2e.ts`'s
  download test, which was right to fail. The endpoint is back to requiring a login and
  nothing more, the behaviour is pinned by a test so it is not "fixed" again, and the
  genuine inconsistency it sits on — the page hides answers from a non-owner while the
  spreadsheet hands them over — is written up in `TODO.md` as a François/Gonçalo
  decision rather than settled by me.
- **`captcha_enabled` defaulted to `True` on `/quiz/start`**, which only looked harmless
  because the single caller sends `'False'`. Any other caller opened a game demanding a
  captcha the join page cannot render and the server cannot verify. It defaults off, and
  it is refused outright when no provider key is configured — so a game that demands an
  uncheckable captcha cannot be created.
- `check_captcha` was worse than the "returns True with no secret" it was filed as: every
  `settings.hcaptcha_key` read was on config.py's *uncalled* `lru_cache` wrapper, so it
  raised `AttributeError` out of `join_game`. Fixed, and it now fails closed with a
  logged reason instead of falling through.

### Tidying

- Fixed a `tike_taken` typo in the results page's prop type, which was one of the
  `svelte-check` errors. The field is never read there, so it only misdeclared the shape
  the server sends (`time_taken`).
- Corrected the `svelte-check` note in `TODO.md` — and then had to correct the
  correction. The real figures, from a **single** run: 1054 errors, **229 ours, 825 under
  `node_modules`**. My first pass read 339/331 from two *separate* `svelte-check`
  invocations, so the two counts never described the same run, and I reported that our
  share was half the problem rather than a fifth. The note I "fixed" (~300 ours, ~820 in
  `bits-ui`) had been right all along. Ours also cluster: the top five files are 81 of the
  229, and three of those are editor parts for question types the MVP does not offer.
- Verified the production build still succeeds after the day's changes (37s), which is
  one of the "Done when" gates on issue #3.

- Removed upstream's results-export route, which sat in the module body as a bare string
  literal that read like a docstring. Uncommenting it could never have worked: it
  referenced three names that do not exist in the module. Kept as a comment recording the
  intended shape, with a pointer to the export that does work.
- The podium printed each place label twice — a visible span plus an `sr-only` copy — so
  a screen reader read it twice at desktop width. One element with `max-sm:sr-only`.
- `anon-game.e2e.ts` had been red since the Kahoot round sequencing landed earlier today:
  it clicked "Next Question" straight after "Show results" and hung on the Scoreboard
  step. The sequence is now a shared helper (`clearScoreboardStep`,
  `advancePastResults`, `advanceToFinalResults`) rather than repeated per spec.

### Uploads: real limits, and no file manager

- **Uploads had no server-side size limit.** The route passed `size = 0` into storage and
  saved `0` on the row, so nothing in the request path ever knew how big a file was; the
  only cap in the product was Uppy's, in the browser, and `POST /api/v1/storage/` takes
  anonymous uploads. One `curl -F` with a 2 GB file filled the volume. Images are capped
  at 8 MB (`max_image_upload_size`), enforced in three places: Caddy's `request_body` on
  `/api/v1/storage/*`, a `Content-Length` check before the body is read, and the route's
  own check on the counted bytes.
- **The browser cap was not applied either.** `restrictions` is an Uppy *Core* option and
  was being passed through the Dashboard plugin, where it appears nowhere in the types —
  so the picker had neither a size cap nor a type filter and would accept an SVG. It is
  on the Uppy instance now, and the numbers come from a new `GET /api/v1/storage/limits`
  so `config.py` is the only place they are written.
- **The per-account quota could not bite**: it was `used > limit`, so an account at zero
  bytes could upload a file of any size, and `used` is maintained by the `calculate_hash`
  worker job, so with the worker down it stayed at zero forever. It is now
  `used + this_file > limit`, and the row records its real size at insert. The quota
  itself drops from ~1.07 GB to 256 MiB — upstream's number was sized for a public SaaS.
- `POST /storage/raw` accepted any `Content-Type`, SVG included, while the route beside it
  enforced an allow-list. Both use one table now, and `/raw` aborts mid-stream rather than
  measuring after the fact.
- `video/mp4` was accepted by the server while `/edit/videos` was hidden and the editor
  passed `video_upload={false}` — an upload path with no UI in front of it. Behind
  `enable_video_upload`, off, with its own ceiling for when it is turned on.
- Two refusals now say something a person can act on: too large, and storage full.
- No file manager, on purpose: a picture belongs to the question it is on. `/edit/files`,
  `/dashboard/files`, the Library tab and Pixabay stay hidden. Written up with every
  number and how to change it in [`docs/uploads.md`](docs/uploads.md).
- `e2e/run.sh` takes `E2E_VENV` to point at a virtualenv directly, for a machine that has
  the dependencies but not pipenv.

### One motion scale, measured rather than asserted

- Motion comes off one scale now. The tree had fifteen different durations and almost no easing: five durations (120 / 200 / 320 / 500 / 750ms, shortest for a control, longest for the podium build) and four curves, declared once in `app.css`. Svelte's JS transitions never see a CSS variable, so the same numbers exist in `src/lib/motion.ts`; `motion.test.ts` asserts the two copies are equal, because two copies of one scale drift the moment nobody is looking.
- Three progress bars animated `width`, which makes the browser lay the page out again for every frame — including the question timer, which redraws every second at the full width of a projector. They animate `transform: scaleX()` off `origin-left` instead, which the compositor handles. `motion.test.ts` now fails the build on any `transition-[width]` or the other layout properties.
- Anyone who asks for less motion gets none: a global `prefers-reduced-motion` block clamps every duration in the scale to 1ms, and `dur()` does the same for the JS transitions, which the media query cannot reach.
- Measured in a browser as well: `e2e/motion.e2e.ts` checks the podium really is held back and then released, that reduced motion really does make it instant, and that the timer is composited rather than laid out.
- Fixed `e2e/global-setup.ts` reading `PW_CHROME`, which nothing sets — on a machine whose only browser is an out-of-tree Chromium, the warm-up pass tried to launch Playwright's own bundled shell and the run died before the first test. It reads `E2E_CHROME`, the same variable the tests use.

### Lobby music, and a medal for the players who placed

- A player who finished in the top three now sees a medal on their own screen at the end — gold, silver or bronze, beside their score. It is the only thing a player carries out of the room, and Kahoot does the same. Below third they get their place in words instead; the two never appear together, because the medal already says the place.

- The lobby plays music again. The track and its uncompressed original have been sitting in `assets/music/` since the fork, REUSE-declared MPL-2.0, with the player commented out in the lobby — a 17-second loop, on at 40% by default, with a mute and a volume slider bottom-left where a room can find it.
- It plays on the host's screen only, in the lobby only. It stops when the first question appears, because that is when the component goes, and it fades rather than cutting — a loop that stops dead sounds like a fault.
- The choice is remembered: a host who turns it off does not fight it again. If the browser refuses to start audio without a gesture — after a reload, say — the control shows a play icon rather than claiming to be on.
- Replaced `audio_player.svelte`, which was a fixed-position pair of hand-inlined Heroicons with a vertical range input, no persistence, no handling of a refused autoplay, and no caller.

### One radius scale, and a stack that starts on Linux and macOS

- The winner is now the point of the podium, not a label on it: their name is the largest thing on the screen and their score sits in a gold pill, while second and third keep the quieter treatment. The podium shape stays, because that shape is what makes an end-of-game screen recognisable — Kahoot shows a leaderboard and then a three-block podium with the winner centred, a crown and confetti, which is what this now is.

- **The host's result download is one press.** "Request result download" minted a token over the socket and renamed itself to "Download results", so one action took two presses — and the hidden anchor that exists to make it one press was bound to a variable and never clicked. The button now says what it does, shows "Preparing the file…" while the token is minted, and starts the download when it arrives. Pinned by `e2e/game-export.e2e.ts`, which asserts a real spreadsheet arrives.
- Fixed the podium's new bottom action row squeezing its second button to nothing: both buttons were `w-full` inside a flex row, which is the trap `CLAUDE.md` lists under "things that keep coming back". `flex-1 min-w-0`.

- The podium and the host's screens now fit a phone. A host can run a game from one, and the actions panel was a 176px block pinned top-right — 44% of a 390px screen, sitting on top of the podium. It is a row along the bottom below `sm`, clear of the safe area, and the podium's blocks keep a usable width instead of stretching into thermometers.
- Pinned it: `podium.e2e.ts` walks the lobby, the question, the per-question results and the podium at 390px and asserts no horizontal overflow at each step, on the host and on the player.

- Corners come off one scale now. Four places rendered a **4px** corner while everything around them was 8–25px: a bare `rounded`, `rounded-t` or `rounded-b` resolves to Tailwind's own `--radius` (0.25rem), which our `:root` override does not reach because Tailwind keeps it in a `reference` layer. The modal in `lib/modals/alert.svelte` was the worst of them — a 14px shell with 4px header and footer rows.
- The landing and join cards were 5.6px rounder than the Card primitive and every other surface; they match now. On the quiz page the question card and the answer tiles inside it were both 19.6px, which reads as two mismatched arcs sharing a corner — the card went up a step. The QR code in the lobby was under-rounded by 17px inside its tile.
- The host's answer row was drawn two ways: 25.2px and palette-coloured for ABCD, 14px on a hardcoded upstream brown with black ink for TEXT. They match, and the brown is gone — it was invisible on a dark quiz background.
- `admin-button` said "same shape as the shadcn primary button" and was 2.8px rounder than it. The description textarea and the rich-text fields were 2.8px rounder than the `<Input>` beside them.
- Added `radius-scale.test.ts`: no bare `rounded` classes, every step derived from `--radius`, and no hand-written `border-radius` outside the token block. Verified it fails by putting one back.
- **`e2e/run.sh` now runs on Linux and macOS as well as Windows.** It finds Postgres wherever the platform keeps it, drops to the `postgres` user when run as root (initdb refuses to run as root, which is how it runs in a container), uses the real `redis-server` when one is installed and falls back to fakeredis, fetches the Meilisearch build for the platform and architecture, and picks Edge on Windows or Chromium elsewhere. `stop.sh` ported with it. Verified end to end on Linux: the whole stack up, 99 specs collected.
- Added `TODO.md`: the live state of the work, next to `MVP.md`, which stays the plan.

### A podium worth waiting for, a join screen worth looking at, and the copy findings

- The podium builds up: third place rises, then second, then first, about 1.4s apart, with a crown on the winner and confetti from both lower corners. It used to put all three up in two seconds. Light goes out of the way of anyone who asks for reduced motion: the whole podium is simply there, and no confetti is fired.
- The blocks are gold, silver and bronze instead of the theme's near-black primary, which made the winner's block a dark slab. Medal colours are what a podium means; they are not a third brand accent.
- Rebuilt the `/play` join screen on the landing page's PIN card: the wordmark, a labelled field with the "enter the PIN from the host's screen" line, and one full-width primary button. It was a floating label, an unlabelled box and a grey Submit on an empty page — and it is the first screen every player sees.
- The host's per-question results and standings are set for a projector at last: at 1920 the question, the answer labels, the counts and the standings scale up instead of staying at laptop size.
- Play is no longer offered to a signed-in visitor on somebody else's unlisted quiz, which the server answers with "quiz not found". The page says why, and points at Practice.
- The navbar's Register link was shown only when registration was *disabled* — inherited inverted from upstream, so the only sign-up link appeared exactly when signing up was off.
- `/explore` is headed Discover, which is what the navbar has called it since the merge.
- Removed "Forgot password?" from the registration form, which is for people who have no password yet.
- The browser-data warning on My Quizzes now appears when there are quizzes to warn about; with none, the empty state carries the sentence instead of stacking two panels.
- Sessions in My Account: the column and badge read "This session" rather than "This session?".
- Deleted upstream's landing-page copy from `en.json` — donations, a German server hosted by netcup, self-hosting, "Multilingual", a community that funds development — along with `landing/landing-promo.svelte`, the dead component that was its only consumer. None of it was reachable, and all of it was false about this product.
- The podium's side buttons are outlined, so "Request result download" reads as a control rather than a line of text on the white podium, and the hidden export anchor is out of the accessibility tree.

### Players are told whether they were right, and hidden pages have a way home

- After each question a player now sees Correct! or Not this time, with a tick or a cross as well as the colour, then the points gained, their total and their place. It used to show "+760" and nothing else, so scoring 0 read as a broken game rather than a wrong answer. Nothing new crosses the socket: the right/wrong flag and the standings were already in what the server sends.
- A player who did not answer in time is told that, instead of being shown "+0".
- The sixteen hidden routes now 404 through the app's own error page, with the navbar, the theme and a Home button. They were guarded in `handle`, which runs before the router, so SvelteKit answered with its built-in fallback: a bare "404 | Not found" with no way out, on exactly the pages we hide. The list moved to `lib/hidden_routes.ts` and `hooks.ts` reroutes them.
- Fixed the editor dropping an edit typed in the first half-second after it opened: the "nothing has changed yet" baseline was taken 500ms late and swallowed the change, so Save sent nothing and still went to the quiz page saying "Saved".

### The editor is one column of question cards (MVP.md D7)

- The editor is now a single scrolling column: quiz setup, then a card per question, then Add. Every question in the quiz is on the page at once, the one you are working on opens in place, and the rest stay as a line of question text with its answers. This is how Google Forms and Kahoot both do it, and it replaces the left rail plus one-question canvas.
- A new quiz shows its title, description and "Add your first question". Cover image, visibility, background colour and background image fold away behind More settings: a new quiz used to open on six fields, four of them decoration, with no question in sight.
- Questions can be added between two others with the + that appears in the gap, duplicated, deleted, dragged by the grip, and moved with the arrows in the card footer. Deleting asks first, because the editor autosaves and there is no undo.
- Added True / False to the question types: an ABCD question that arrives with True and False already written and True marked correct. No new backend type, no new play, scoring or export path.
- The quiz title and each question's text now have real accessible names ("Quiz title", "Question text"). CKEditor labels every instance "Rich Text Editor", which told a screen reader nothing once more than one was on the page.
- Removed `editor/card.svelte`, `editor/sidebar.svelte` and `editor/question-strip.svelte`, which the column replaces.
- Fixed an `<input type="color">` that was handed an empty value, which logged a format warning on every editor load.
- Added `e2e/editor-column.e2e.ts`: one card open at a time, insert in the middle, True/False, duplicate, move, delete, and the phone layout.

### Hosting is a first-class choice on the landing page, and three plural strings printed their key

- Added `docs/audit-2026-10-01.md`: the full assessment — every route probed against the running app and classified, all three suites run, every page screenshotted at 390/834/1440 in both themes plus the live game end to end, the findings, and where each item on the shared to-do list actually stands.

- The landing page's three muted text links under the PIN box became two secondary buttons, Create a quiz and Go to your quizzes, under a "Running the quiz?" divider, with a line saying no account is needed and that browser quizzes are deleted after 30 days. Making a quiz now reads at the same level as logging in, which is what it is: it needs no account.
- The navbar shows a Create a quiz button beside Log in for signed-out visitors, on desktop and in the mobile menu.
- Fixed three places that asked i18next for a `*_plural` key, which has not existed since i18next v20: the host lobby's player count and the host's per-question results both printed `play_page.players_waiting_plural` on the projector, and every quiz card on My Quizzes printed `words.question_plural` instead of "Questions". The `_one` / `_other` keys they should have used were already in `en.json`.

### Editor autosave and drafts (MVP §4.5, D14)

- The editor now autosaves to the server a couple of seconds after you stop typing, once the quiz has a title and a question. A new quiz is created on its first save, and the address changes to its edit page, so a reload reopens it. Back saves before leaving.
- Nothing is marked red until you first press Save. Save on an unfinished quiz keeps it as a draft and says how many questions are left; on a finished quiz it goes to the quiz page as before.
- A quiz with an unfinished question is a draft. The server refuses to start one, and the quiz page and My Quizzes show a Draft badge with Play disabled. There is no new database column: draft is worked out from the questions, by the same rule in the editor and on the server.
- Old quizzes with TEXT, VOTING or ORDER questions are no longer flagged as unfinished. The completeness check only knew the ABCD rule, and with Start now enforcing it those quizzes would have become unplayable.
- The description is optional, and the field says so and has a placeholder. It used to be required, at least three characters, and nothing on the page said so.
- The search index is now updated after a quiz is saved, not before, so it no longer lags one save behind. An edit session also stays alive while autosave runs, where it used to expire after an hour, making Save fail with "Edit ID not found".
- CHECK answers now get the same HTML cleaning on save as ABCD answers.
- The question-limit message said 32 while the limit is 50; it now says 50.
- Starting a game that the server refuses now shows the server's reason instead of a generic failure.

### Practice rebuilt, Download is Excel only (MVP §4.4, D3 and D5)

- Rebuilt Practice. Picking an answer threw an error, because every answer loop referred to an `i` that was never declared, so practice had never worked. It also leaked a timer per question and reshuffled the quiz it was showing. It now uses the live game's answer tiles, has no timer, reveals ABCD answers on click, lets you tick CHECK answers and then submit, scores with the game's rules, and ends on a score with Practice again and Back to quiz. Question types the MVP doesn't offer show a notice and a Next button.
- Rebuilt the Download dialog on shadcn `Dialog`, offering Excel only (D5). It was a `w-1/3` overlay, about 130px wide on a phone.
- Fixed three Excel export bugs: CHECK questions were left out, question text came out as editor HTML, and a fifth answer overwrote the time limit column. The file is now served as `.xlsx` rather than the old `.xls` type, and it is named after the plain title.
- Added `practice.e2e.ts` (practice end to end, a missing quiz, and the Download dialog fetching a real spreadsheet), unit tests for practice scoring, and backend tests for the Excel rows.

### MVP hides, "Unlisted", and the security items (MVP §4.2, §4.3, §4.6)

- Hid Import, Results history, Analytics, the Files library, `/remote`, public profiles and the avatar editor (decisions D4, D6 and D15). Each hidden route now 404s through `DISABLED_ROUTES`. The My Quizzes toolbar, the Analytics row button, the podium's Save results button, the Import/Results command-palette entries and the My Account avatar/profile buttons are commented out rather than deleted. The APIs behind them stay up.
- Renamed the settings page to My Account: heading, tab title and command palette.
- Relabelled "Private" as "Unlisted" (D13). A private quiz was always openable by anyone with its link, so the old word promised something the app never did. The editor's toggle now uses a link icon instead of a lock, and adds a line saying that Unlisted quizzes open only by link.
- Fixed the join-time captcha check never running: `check_captcha` is async and was called without `await`, so it returned a coroutine, which is always truthy, and every captcha passed. It is inert today because captcha is off, but it would have been a bypass the day captcha was turned on.
- `/api/v1/internal/testing` is now mounted only when `ENABLE_TESTING_ROUTES` is set, which only `.env.ci` does. It returns a full user row, password hash included.
- Put adding a WebAuthn key behind `ENABLE_WEBAUTHN` and quiz rating behind `ENABLE_RATINGS` (D11), both off by default. Existing keys can still be listed, deleted and used to sign in. CI turns both on, so the code stays tested.
- Switched off the IP-lookup endpoint behind `ENABLE_IP_LOOKUP`. Nothing calls it, and its provider sent the lookup over plain HTTP. Its test used to call ip-api.com from CI; it now checks that the endpoint is off.
- Added CodeQL (Python and TypeScript, on push, on PRs and weekly) and Dependabot (pip, npm, GitHub Actions and Docker, with minor and patch bumps grouped).
- Added `hidden.e2e.ts`, which checks that every hidden route 404s, that the legal pages stay up, and that no navbar, footer or toolbar link points at a hidden page.

### Docs and GitHub hidden; MVP decisions recorded

- Hid Docs and GitHub from the navbar, the command palette and the footer. The footer now links Terms of Service, Privacy and Attribution in their place.
- `/docs` and upstream's self-host, develop, roadmap, pow and markdown doc pages now 404 through `DISABLED_ROUTES`. Those pages also stopped being prerendered: a prerendered page is served as a static file that never reaches the guard. The legal pages stay up.
- Recorded Gonçalo's 2026-09-29 decisions in `MVP.md`:
  - D2: question types are ABCD and CHECK.
  - D4: hide Results, Analytics and Save results.
  - D5: Download keeps Excel only.
  - D6: hide Import.
  - D9 and D11: confirmed.
  - D10: English only, keeping the i18n machinery, with more languages as an MVP2 item.
  - New D13: "private" is relabelled "Unlisted".
  - New D14: the editor autosaves drafts to the server.
  - New D15: hide `/remote`, public profiles, the avatar editor and the Files library.

### My Quizzes: one page for everyone (MVP decision D1)

- Merged `/dashboard` into `/my-quizzes`. Signed out, it lists this browser's quizzes, with the MVP's plain explanation that they are tied to this browser and deleted after 30 days, and a "Create a free account to keep them" button. Signed in, it lists the account's quizzes, with this browser's anonymous ones underneath under "On this browser", each with a Claim button.
- Every row has Play, Edit and Delete, whether signed in or not. The signed-out list used to be titles only. Account rows keep Analytics and Download. The title links to the quiz's view page, which replaced the separate View button.
- Delete now asks in a dialog instead of `confirm()`, and removes the row without a page reload. A failed delete or claim shows its error on that row.
- `/dashboard` is now a 302 to `/my-quizzes`, and `/overview` points there too. So do the signed-in redirect from `/`, the login page's default destination, and the register, resend-verification and reset-password redirects. Every in-app link to `/dashboard` was repointed, including the command palette, the start-game dialog's sign-in link, `/import`, `/results` and the view page.
- Moved `Analytics.svelte` from `routes/dashboard/` to `lib/dashboard/`, since that route is now only a redirect.
- `/create` works signed out without `?anon=true`. Before, plain `/create` sent a signed-out visitor to the login page, which would have walled off the new signed-out Create button. Old `?anon=true` links still work.
- Saving in the editor now always lands on the quiz's view page. A signed-in edit used to go to the dashboard, while everything else went to the view page.
- Dropped the Settings button from the My Quizzes toolbar, since it is My Account in the navbar now. Import, Results and Files stay until decisions D4 to D6.
- Fixed "Expires in 31 days" on a quiz saved a moment ago. The server adds 30 local days, a window that crosses the October clock change is 30 days and an hour long, and the rounding was `ceil`. It is now one shared helper that rounds and never says 0 days while the quiz still exists, with a unit test that fails under the old rounding.

### Navbar: Discover · My Quizzes · Join

- The navbar now shows Discover (`/explore`), My Quizzes and Join (`/play`) for everyone, signed in or not. The current page is marked with `aria-current` and a muted pill. The Play pill that was highlighted on every page is gone.
- Signed-in users get a My Account link beside Log out. Docs and GitHub still show for signed-out visitors: removing a navbar tab is a joint François/Gonçalo decision, so it waits.

### Ways out of a live game (MVP §4.3)

- The host can cancel a game from the lobby, after a confirm. A new `end_game` socket event deletes the game's Redis state, then tells everyone: the host lands on My Quizzes, players see "The host ended the game", and the PIN stops resolving. It refuses to cancel a game that has started.
- The host can end a game mid-way with an End game button (with a confirm) that goes straight to the podium. The podium's Back goes to My Quizzes for everyone; for anonymous hosts it used to go to `/`.
- Players can leave from the join screen, the lobby and between questions, after a confirm. A new `leave_game` socket event frees their nickname and removes them from the host's list. If the leaver was the last player who hadn't answered, the question closes as if everyone answered.
- The join screen has a Home link. It shows wrong-PIN, already-started, taken-nickname and kicked errors inline instead of in `alert()` boxes. The nickname minimum is now 2 characters (it was 4, with no explanation), and a hint says so.
- The host screen's registration error (for example, the game already open in another tab) used to be a bare red line with no navbar. It now has a Back button to My Quizzes.
- Added the reusable `ConfirmAction` component (a button that opens an `AlertDialog` before acting), used for all of the above and for My Quizzes' Delete.

### End-to-end suite

- Added `game-exits.e2e.ts` (five UI tests for the exits above), a `leaving` block in `live-socket.e2e.ts` (five socket-level tests) and `my-quizzes.e2e.ts` (four tests: the redirects, the navbar indicator, signed-out delete, and signed-in claim).
- Updated the existing specs for the renamed routes, the collapsed anonymous banner and the view page's Play button. The full suite passes locally: 77 of 77.
- `e2e/run.sh` and `e2e/stop.sh` take `E2E_DATA` and `PG_PORT` overrides, so two stacks can run side by side without fighting over Postgres. `.gitignore` covers `e2e/.data*/`.
- Recorded a race found on the way in `docs/e2e-findings.md`, not fixed. Host socket events each read-modify-write `game:{pin}`, so a `set_question_number` racing `start_game` can lose the `started` flag.

### View page redesign (`/view/[quiz_id]`, #17)

- Rebuilt the quiz view page on shadcn `Card`, `Collapsible`, `Badge` and `AlertDialog` in a `max-w-2xl` reading column, replacing `bg-white dark:bg-gray-700`, the blue/yellow correct-answer shadows and the `bg-gray-300` answer rows with theme tokens.
- Made Start the one primary action. Edit (new on this page) and Delete appear only for the quiz's owner, whether that's an account or the browser that created it anonymously. Practice and Download stay where they were, pending decisions D3 and D5.
- Replaced the "you need to be logged in" tooltips on the disabled Play and Download buttons with a visible line of text, since a tooltip on a disabled button can't be reached by tap or keyboard.
- Moved the anonymous-quiz notice to the top of the page as an expandable banner. Collapsed, it still says the quiz isn't saved and how many days are left; expanded, it gives the full explanation and the sign-up or claim button. A failed claim now shows an inline error instead of a browser `alert()`, and delete confirms in a dialog instead of `confirm()`, staying open with the error if it fails.
- Replaced the full-width collapsed question bars with the editor's own question layout, read-only and always open: "Question n of total" with time and single/multiple-answer above a card holding the centred title, the image and the real answer tiles with their shapes. The correct answer carries the editor's ring and tick. The range-question sentence moved into `en.json`, and the unused `?autoExpand` parameter was dropped.
- Only the quiz's owner sees the answer key on the view page: the correct-answer ring and tick, a range question's correct bounds, an order question's sequence (visitors get the items alphabetised) and a text question's accepted answers. The public API still returns them, so this is about not spoiling the quiz, not about secrecy.
- Recorded Gonçalo's positions in `MVP.md`: D1 (one `/my-quizzes` page), D7 (continuous editor list), keep and redesign Practice (D3) and Download (D5), and a new D12 for owner-only answers. François's sign-off is still open on all of them.
- The author's name no longer links to `/user/[id]` (public profiles are hidden for the MVP), and the quiz description, question count and public/private state sit in one metadata row.
- Removed a stray `console.log`, a document keydown listener that was never removed, and the old `lib/collapsible.svelte`, whose only consumer was this page.

### MVP checklist

- Added `MVP.md`, a shared checklist for Gonçalo and François. It has a Keep/Merge/Hide/Remove/Investigate audit of every route, the proposed Discover | My Quizzes | Join structure for anonymous and signed-in users, findings on Import and the Files library, eleven decisions to sign off, and the work and play-test matrix still needed before sharing frogQuiz.

### CI: an unresponsive S3 backend could hang a job for its full 10-minute timeout

- `S3Storage.__init__` built its `minio.Minio` client with the library's own default -- a 5-minute connect *and* read timeout, 5 retries -- and called `bucket_exists()`/`make_bucket()` on it synchronously, with no `await`, straight out of `__init__`. A backend that accepts the connection and then simply never answers (rather than refusing or erroring, which fail fast) blocks the whole event loop for as long as that takes. `test_minio` hits a public demo endpoint, `play.min.io`, for exactly this reason, and twice in a row it ate an entire CI job's 10-minute timeout before the runner killed it -- not a test failure, a stall with no error message. Gave the client an explicit 15-second connect/read timeout instead (production S3-compatible backends answer in milliseconds; this is generous) so an unreachable backend now fails fast and clearly, in test or in production, instead of hanging silently.
- Even bounded, `play.min.io` stayed unreachable from GitHub's runners across three separate CI runs (identical `ConnectTimeoutError` each time) -- an outage of a public demo server this repo doesn't control, not a flake and not fixable from here. Skipped `test_minio` (François's call, not a unilateral one) rather than leave CI permanently red on it. The skip names what would replace it: a real MinIO service in `docker-compose.dev.yml` alongside `db`/`redis`/`meilisearch`, the way `run_tests.sh` already stands the others up, so the S3 backend has local coverage that doesn't depend on a third party's uptime.

### Account management: verification, password change, and a delete-cascade audit

- **Clicking an already-used confirmation link told a verified account its link was dead.** `GET /verify/{key}` nulled `verify_key` on success, so any second visit to the same link -- a double click, a mail client that pre-fetches links, reopening the confirmation email days later -- was indistinguishable from a genuinely bogus one and landed on "that link isn't valid, request a new one." Worse, following that advice did nothing: `resend_verification` only sends when the account isn't already verified. The key now survives a successful verify (idempotent: revisiting it just redirects to the "verified" state) and is only invalidated by `resend_verification` actually minting a new one, so a superseded link still correctly expires. Verified with a live server: registering, clicking the link three times, and confirming each visit -- and a genuinely superseded link -- behave correctly; covered by a new test, `test_verify_email_repeat_click_and_supersede`.
- **The change-password form on `/account/settings` had no error handling for a network failure** -- the `fetch` wasn't wrapped, so a dropped connection rejected into nothing and the button just sat there with no feedback. It also had no loading/disabled state (every other form on this surface does), so a double click could fire the request twice, and every failure -- wrong password, rate-limited, a dropped connection -- showed the same generic message. Now wrapped in try/catch, disables and spinners while in flight, and shows a specific message for a wrong current password (400) vs. too many attempts (429) vs. anything else.
- **The same form was shown to OAuth accounts**, which have no password to change (`frogquiz/oauth/*` creates them with `password=None`) and always got the generic failure message on submit. It's now hidden behind the same `auth_type !== 'LOCAL'` check `delete-account.svelte` already used, with an explanatory line in its place.
- **A session with no ordinary browser User-Agent** (an API key, a script, curl) rendered as the literal string "undefined undefined (undefined)" in the settings page's sessions table. Falls back to "Unknown device" now.
- **The delete-account dialog's Cancel button rendered the literal text `words.cancel`** -- that i18n key never existed. Added it.
- `getUser()`'s 401 redirect on `/account/settings` dropped the visitor straight to `/account/login` with no `returnTo`, unlike the sessions-list 401 two lines below it, which does; now consistent.
- Audited the delete-account cascade end to end: read every `ON DELETE` rule referencing `users` (all `CASCADE` except `storage_items`, which is deliberately `SET NULL` plus an explicit app-level file delete -- see `delete_user_account`), then verified live against a running server that deleting an account with a quiz, an API key and a session attached leaves zero rows behind in `users`, `quiz`, `api_keys` and `user_sessions`. No gaps found.
- Everything else on this surface -- registration (duplicate email/username, case folding, the 32-character username trap, rate limits), forgot/reset password, resend-verification, sign-out-everywhere, and the delete-account confirmation flow itself -- was reviewed against the running app and found already correct; no changes needed there.

### Second round of manual-testing fixes

- Fixed image uploads still doing nothing after the previous round's backend fix. The fix itself was correct; `e2e/run.sh` starts uvicorn without `--reload`, so the API process was serving two-hour-old code and every upload was still answering 401. Documented the trap in `docs/e2e-findings.md`.
- Fixed the uploader closing its dialog and reporting success on a failed upload. It wrote `undefined` into the quiz and closed regardless of `result.failed`, which is what made the 401 above invisible three times over. It now only commits when an upload actually succeeded and an id arrived, and otherwise leaves the dialog open showing the error.
- Fixed the uploader's file restrictions never being applied: the options were passed as `properties`, which `@uppy/svelte` does not read (it is `props`). Narrowed the accepted types from `image/*` to the four the server accepts, so the picker stops admitting files it will answer 422 to.
- Removed a duplicate Uppy Dashboard instance. The plugin was installed manually as well as by the Svelte component, leaving three to four dashboards in the DOM, two upload buttons, and the image editor attached to an invisible one.
- Moved the editor header's error message back to the right of the row. The previous round gave it `flex-1` so a long title could not squeeze it out, which fixed the width but left it reading as trailing the title rather than sitting at the end of the header.
- Fixed per-question titles rendering their raw HTML (`<p>test</p>`) in ten places. They come from the same rich-text editor as the quiz title, but only the quiz title had been sanitized — the editor rail, the filmstrip, the player and host question screens, per-question results, practice, remote and results history were all showing markup.
- Fixed a blank question passing validation: `questions[].question` was length-checked on raw HTML, and an emptied rich-text editor hands back `<p></p>`, which `trim().required()` accepted as six characters. A question that was blank on the projector could be saved.
- Rebuilt the post-save page's bento grid. The anonymous-quiz notice was a grid tile, so its ~350px of prose dictated the row heights, spreading Practice and Download ~360px apart, and its "Create an account" button clipped inside a too-narrow track. The grid now holds actions only, with fixed row heights, and the notice sits below it.
- Stopped the host's start-game "custom field" inheriting a stale value from `localStorage`. A value typed once re-applied to every later game, so players were shown the host's email address as the heading over a second, unexplained input box. The field is now an explicit opt-in that starts empty.
- Gave the join screen real `<label>`s, a length cap on the custom field matching the server's, and `autocomplete="nickname"` on the nickname input — with no autocomplete token browsers offered a saved email address for it.
- Fixed the player's per-question results screen sitting flush against the top of the phone. The score card was centring itself inside its own `h-screen` block while the heading sat above it; the card now only draws itself and the route's `fq-stage` places it.
- Replaced the remaining `min-h-screen` on the play route and the join screen with the `dvh` equivalent, so the submit button and score card are above the fold with mobile browser chrome present.

### Fixed a batch of bugs found by manual testing (anonymous create/edit/play flow)

- Sanitized the quiz title (a rich-text field) instead of storing/displaying its raw HTML unfiltered. A pasted `<p>`/`&nbsp;` or foreign markup used to show up as literal text in the editor sidebar and header; bold/italic/etc. now render correctly everywhere the title is shown (editor, live host screen, search results), while non-toolbar tags and pasted CSS text are stripped.
- Trimmed the "Select the Upload Type" modal (cover image, background image, and question media) down to Image only. Video, Library, and Pixabay are hidden, not deleted, per the feature-triage rule — clicking "Add Media" now skips straight to the uploader instead of showing a picker with one real option.
- Fixed image uploads doing nothing for an anonymous host: `POST /api/v1/storage/` required a logged-in user, with no allowance for the anonymous-quiz flow that already works everywhere else in the editor.
- Redesigned the post-save quiz page's action area as a bento-style grid, with Play as the large primary tile (now labeled "Play" instead of icon-only) and Practice/Download/account-status as smaller tiles.
- Removed the drop-shadow/glow under answer-option tiles on both the host and player live-question screens.
- Fixed the host's live per-question results card: it used the dark-mode-following `bg-card` token on a card meant to sit on the quiz's own background colour, making it unreadable in dark mode. It's now a fixed light "paper" surface. Also fixed the card's oversized empty space, caused by a redundant `fq-stage` nested a second time inside the results card.
- Added a "Back" button to the podium/final-results screen, routing to the dashboard (signed in) or home (anonymous) — previously "Download results" was the only action, leaving the host stuck.
- Tightened the quiz title limit from 300 to 100 characters (measured on visible text, not markup) and added a live character counter with an inline warning for both title and description, instead of only failing at Save.
- Fixed the editor header's error indicator being squeezed unreadable next to a long title by giving the title a width cap and the error message its own share of the row.
- Fixed single-correct-answer (ABCD) questions allowing more than one answer to be marked correct; marking a new one now unmarks the rest, with the same normalization applied server-side as defense in depth.

### Fixed every bug the e2e suite found

Details, and how each was fixed, are in `docs/e2e-findings.md`. All 63 e2e tests pass. The backend suite's failures are identical to a clean-HEAD baseline in the same environment.

- Fixed lost answers when players answer together. Answers are appended in a Redis transaction, and the duplicate check runs inside it. 50 simultaneous answers now keep all 50, where they used to keep 1–2. The box-controller path uses the same helper.
- Fixed players who reload being unable to score: `rejoin_game` saves the session before it syncs time.
- Closed two ways for a player to take host control. `register_as_remote` now needs the host's `game_id`. `GET /quiz/join/{pin}`, which handed that `game_id` to anyone with the PIN, now answers 410. `game_id` is no longer sent to players in the game object.
- `submit_answer` refuses answers after the timer (plus 1.5 s of grace) or once results are showing, and a score can no longer go negative.
- Kicked players can no longer rejoin, and a nickname is claimed atomically, so two players can't join under the same name.
- Game events are scoped to their game's rooms. They used to broadcast to every connected client.
- The server rejects quizzes that can't be played: no questions, a question with no answers, more than 10 answers, or a timer that isn't a number between 1 and 999 s. Starting an empty quiz returns 400.
- Anonymous quizzes can be reopened in the editor (`/quiz/get` accepts the anonymous secret). The edit page shows an error instead of going blank.
- Signing in no longer locks you out of a quiz you made anonymously: start, delete and get check the account and the secret independently.
- The projector podium rebuilds its totals from the server's final results.
- The editor blocks Save while a question is incomplete and says how many. Its Back link goes to `/my-quizzes` for someone without an account, and saving an anonymous quiz returns to its view page.
- Signing up from "keep this quiz" now leads back to the quiz, because `returnTo` is carried through to the login link.
- The login page only follows a `returnTo` that stays on this site. It used to follow any URL, an open redirect.
- A player can reload more than once (the rejoin cookie is refreshed), gets the current question back after a reload, and the cookie now lasts 5 hours instead of about 10 years.
- The end screen shows "Your score" for a player on 0 points. The podium no longer shows the raw key `words.point_plural`. Fixed "1 Answers submitted" and "1 player are waiting".
- Removed every `test.fail` marker. The tests stay as regression guards, and new unit tests cover the podium totals and `returnTo` handling.

### Local end-to-end test harness (no Docker, no WSL)

- Made the E2E launcher resolve the Pipenv environment correctly from Git Bash on Windows.
- Added `bash e2e/run.sh`, which brings up the whole stack on Windows from what is already installed: a throwaway Postgres cluster on 5433, fakeredis on 6380, a portable Meilisearch exe (downloaded once into `e2e/.tools`), the API on 8010 and vite on 3000. It then runs Playwright against the installed Edge and tears everything down afterwards. All state goes in `e2e/.data` (gitignored) and is wiped on the next run.
- Added `@playwright/test`, `frontend/playwright.config.ts`, and seven specs under `frontend/e2e/` (`*.e2e.ts`, so vitest ignores them):
  - `anon-game`: a full anonymous game in real browsers.
  - `api-edge`: malformed and extreme API input, and anonymous ownership.
  - `live-socket`: a 50-player crowd, and join, answer and host-control rules at the socket level.
  - `editor`: building, validating, editing and saving a quiz by hand.
  - `account`: register, log in, dashboard, claim, Explore, saved results.
  - `game-reload`: player and host reloads mid-game.
  - `responsive`: the overflow sweep at 390/834/1440 and the theme toggle.
- Added `e2e/stop.sh` for stacks left up with `KEEP_UP=1`, and a Playwright global setup that warms Vite's on-demand route compiles so a slow first compile doesn't read as a test failure.
- Wrote up every bug the suite found in `docs/e2e-findings.md`: 6 high, 12 medium, 6 low, plus UX notes and what held up. Each bug a test can reach is a `test.fail`, so the run stays green and a test flips red once its bug is fixed. Nothing in the app was changed. The worst:
  - concurrent answers overwrite each other;
  - a player who reloads can never score again;
  - any player can take host control, through `register_as_remote` or the `game_id` from `/quiz/join/{pin}`;
  - anonymous quizzes open to a blank editor.
- Added P0/P1 items for those bugs to `BACKLOG.md`, and replaced its "there is no local backend" constraint, which no longer holds.
- CLAUDE.md: added a section on running the e2e suite. Also corrected the background check in "Verifying UI changes", which read `body` (transparent by design) instead of `html`.
- Added `e2e/shims/magic.py`, a test-only stand-in for python-magic, whose Windows DLL crashes on import.
- `e2e/e2e.env` turns off the signup email deliverability check (a live MX lookup), so runs need no DNS.

### Host start-game modal rebuilt on shadcn

- Rebuilt `lib/dashboard/start_game.svelte` on shadcn `Dialog`/`Button`/`Input`/`Label`/`Switch` (the last newly added to `frontend/src/lib/components/ui/`). It was the last pre-redesign surface in the host path: a hand-rolled `<div>` overlay with its own Escape/backdrop handling, hardcoded `w-screen`/`h-screen`/`text-black`/`bg-white`/`bg-green-500`, and `marck-script` on the CTA.
- Dropped the Normal/Old-School game-mode picker — Old-School was never used, so the modal now always sends `game_mode=kahoot`; the API still accepts `normal` if that's ever wanted back. Also dropped the captcha toggle, which was dead UI while hCaptcha is off at the config level.
- The start request built its query string by interpolating `custom_field` directly, so an `&` in it silently truncated the value and a `#` dropped everything after it from the request entirely. Now built with `URLSearchParams`.
- The failure path was a bare `alert()` that then bounced to `/account/login` on *any* non-200 whenever there was no anonymous secret — so a 500, a rate limit, or a quiz deleted in another tab all threw a signed-in host out of the page as though their session had expired. Now only an explicit 401/403 redirects; other failures show an inline message, with a sign-in link when a 404 for a non-anonymous caller suggests an expired session.
- Tracked as [ogfrench/frogQuiz#16](https://github.com/ogfrench/frogQuiz/issues/16). Not yet driven in a browser at 390/834/1440 — no local backend and no headless-browser tooling in this environment; batched into the standing visual-pass item ([#19](https://github.com/ogfrench/frogQuiz/issues/19)).


### Security: quiz text was rendered as HTML

- Quiz titles, descriptions, question text and answer text were rendered with `{@html}` in 28 places across 19 components, so anything an author typed ran as markup. This reached every surface that shows a quiz: the search and explore cards, the public quiz view page, the dashboard, the player's phone and the host's projector during a live game, the practice and remote modes, and the results history. Since `/create?anon=true` needs no account, planting it needed no account either. All 28 now use plain interpolation, which Svelte escapes.
- The four `{@html}` calls left are deliberate and none render author text: the QuizTivity markdown components (which render markdown on purpose, and are behind a disabled feature), a popover that is only ever passed a translation string, and an i18n sentence with interpolation.
- The search and explore cards are the one place that genuinely needs markup, because Meilisearch marks matched terms with `<em>`. `lib/search/highlight.ts` now escapes the field first and restores only that one tag pair as `<mark>`; the author-controlled half cannot survive as markup. The old code rewrote `<em>` in the raw response text before parsing, which rewrote it anywhere in the payload and escaped nothing.
- Removed the author name from `{@html}` entirely -- it never contained highlights.
- `GET /api/v1/quiz/get/public/{id}` returned `anon_secret`, the stored ownership hash, on an unauthenticated response. It is a SHA-256 of 256 random bits so it was not reversible, but it is a credential and is now excluded from the response model.


### Player nicknames were unbounded

- `JoinGameData.username` was a plain `str`. The join form caps it at 17 characters, but the socket server is reachable without the form, so nothing server-side bounded what arrived -- a crafted client could join with a 100,000-character nickname, an empty one, or one containing newlines and null bytes. A nickname becomes a Redis key, a member of the player set and a line on the host's projector, so that was a way to bloat Redis and break the display for everyone else in the room. Nicknames are now trimmed, stripped of control characters, required to be non-empty and capped at 50 characters; `custom_field` is capped at 200. The server bound is deliberately looser than the form's so it can never reject someone the UI let through.
- `RejoinGameData.username` is cleaned identically, or a rejoin would look up a key the join path could never have written.
- The join form now trims before its own length check. Untrimmed, four spaces passed as a nickname, which the new server-side rule would then reject with nothing shown to the player.


### Anonymous quizzes

- `DELETE /api/v1/quiz/delete/{quiz_id}` now accepts `X-Anon-Secret` in place of a login. Delete was the one thing the anonymous creator could not do -- they could edit and host a quiz made at `/create?anon=true` but never remove it, so the only way back from a mistake was to wait out the 30-day sweep. A wrong secret and an unknown quiz both 404, matching `/claim`, and the anonymous path is scoped to `user_id=None` so a stale secret can never delete a quiz that has since been claimed.
- The quiz view page now tells the anonymous holder when the quiz expires and what to do about it: claim it if signed in, create an account if not, or delete it now. Previously the expiry was invisible and the quiz simply vanished.
- Added `/my-quizzes`, a per-browser list built from the stored secrets, linked from the landing page. `localStorage` was the only record of an anonymous quiz, so closing the tab left it unreachable until the sweep. Dead entries are pruned when the quiz 404s.
- Extracted `collect_quiz_image_keys` in `frogquiz/helpers`; the delete endpoint and the expired-quiz sweep each carried their own copy of the storage-key regex and the imgur exclusion. Deliberately unchanged: only question images are collected, not `cover_image`/`background_image`, because neither caller has ever deleted those and widening what a delete removes is not a change to make in passing.


### Scope

- Added an "MVP1 working set" section to `BACKLOG.md`, ahead of the MVP2 list: the anonymous host's login wall (P0), the Explore/Search merge and play/host UX (P1), and the dashboard merge, play modal, view-page design and editor add-button (P2). Records Gonçalo's position on feature consolidation as his position, since `CLAUDE.md` makes the blanket form a joint call with François.

- Settled that an account is what makes a quiz permanent, not what lets you use the app: no account to create, host, share a PIN or play; an account to make a quiz permanent, searchable and manageable. Recorded in `docs/mvp-scope.md` along with the two rejected alternatives (public searchable anonymous quizzes, and free-text author names) and what each would have cost.
- Settled that `public` keeps meaning world-visible for MVP1. Marking a quiz public publishes its title and description to anyone on the internet; quizzes are private by default, so this only affects ones somebody deliberately made public. Recorded as a known property with the two ways out if it stops being acceptable.


### Hosting a game: the modal, and parity between the two kinds of host

- The start-game modal was rebuilt on the shadcn `Dialog`, `Switch`, `Input` and `Label`, dropping the `w-screen h-screen … text-black` overlay, the hardcoded white/green/blue, the untranslated strings and the `alert()` failure path. It also drops the Normal/Old-School mode picker (game mode is hardcoded to `kahoot`; the API still accepts `normal`, so it can come back without a backend change) and the captcha toggle, which was dead UI while hCaptcha is off at config level.
- **The custom field was not URL-encoded.** It was interpolated straight into the query string, so an `&` typed into it started a new parameter and truncated the value, and a `#` made everything after it a fragment the server never saw. It goes through `URLSearchParams` now.
- **Failing to start a game logged you out.** Any non-200 response sent the host to `/account/login` whenever there was no anonymous secret — so a 500, a rate limit, or a quiz deleted in another tab all threw a signed-in host out of the page as though their session had expired. Only an explicit 401/403 does that now; a 404 without a secret says the session may have lapsed and offers a sign-in link, and everything else shows the inline error.
- The modal is no longer wrapped in `{#if quiz_id !== null}` at its call site. It is a `Dialog` and owns its own visibility, so the wrapper meant it appeared already-open with no enter animation and unmounted before the exit one could run. A stale error from a previous quiz no longer survives into the next open either.
- **The lobby's fullscreen QR overlay was `w-screen h-screen`** — 100vw includes the vertical scrollbar, so it overflowed by that width on any page that scrolls, and 100vh is the wrong number on a phone. Now `inset-0`. The two `bg-white` uses around the QR code are deliberate and now say so in the file: a QR code needs a light quiet zone to scan in either theme.
- The host shell used `min-h-screen`, which is `100vh` and has the same phone problem as `h-screen`. Now `min-h-dvh`.
- `slide.svelte` and `voting_results.svelte` were the last two host surfaces outside `fq-stage`, so they sat flush against the top of the projector with the bottom half empty. Both are in it now. The slide image was sized `h-full` against a parent that no longer has a fixed height, so it is capped at `70dvh` and centred by the stage instead.
- Recorded the anonymous-versus-signed-in host differences in `docs/redesign-status.md`, each checked against the endpoint rather than assumed. One assumed difference turned out not to exist: there is no "resume lobby" card for anyone, so anonymous hosts are not missing one.


### Issue tracker

- Recorded the MVP1 working-set progress on GitHub. Status comment on the MVP1 umbrella (#3), and three new sub-issues: #17 (view page), #18 (dashboard merge), #19 (the outstanding 390/834/1440 visual pass).
- The "play modal front-end fix" that `BACKLOG.md` carried as blocked on a decision is **#16**, which specifies it as the host's start-game modal — the same component the play/host UX item has to rebuild. The two are one piece of work now. #16 also carries a scope cut this backlog entry did not: drop the Normal/Old-School mode picker and the dead captcha toggle.
- #13 already described the account-deletion foreign-key and storage-leak bugs fixed here, which were found independently while auditing foreign keys. Commented rather than duplicating, noting that the fix also covers `rating.quiz` — which #13 missed, and which broke ordinary quiz deletion for any rated quiz, not just account deletion.


### Backlog

- `BACKLOG.md`'s MVP1 working set now opens with a status table — three items done, one next, three open, one blocked on a decision — and records the two verification constraints that shaped how each was checked: there is no local backend, and the Vite proxy cannot reach the deployed one from this environment because TLS interception breaks the certificate chain. The play/host and view-page items were filled in with what reading the files actually turned up, so neither starts from a one-line description.


### Docs corrected

- `docs/redesign-status.md` claimed `/view/[quiz_id]` had been "reviewed and needed no change". It had not: the page still carries `bg-white dark:bg-gray-700`, hardcoded blue and yellow shadows, a hand-rolled collapsible and an icon-only Play button with no accessible name. Corrected, and the two surfaces touched here are listed as redesigned-but-not-yet-driven rather than promoted to Done, which on that page means a real browser at 390/834/1440.
- `CLAUDE.md`'s note that Explore and Search are coupled through `search-card.svelte`'s use of `explore_page.*` is no longer true and says so. The removal surface below it is unchanged, and deleting either remains a joint call.


### Explore and Search are one page

- `/explore` and `/search` were two pages posting to the same Meilisearch endpoint with two different bodies — Explore sent `{q:'*', sort:['created_at:desc']}`, Search sent `{q, attributesToHighlight:['*']}`. They are one page now, and `?q=` picks the mode: absent or empty browses the newest quizzes, three characters or more searches, and one or two characters sends no request at all. The URL is the state, so Back, Forward, reload and a shared link all work — the old page kept the term in component state and pushed history by hand, so Back changed the address bar and left the results alone.
- `/search` still exists and 302s to `/explore`, carrying `?q=` across, because those links have been shared. Its 119 lines — a client fetch, an `onMount`, a hand-rolled `pushState` and a hardcoded English empty state pointing at `/import`, which needs an account — were deleted rather than ported. The empty state now offers `/create?anon=true`, which does not.
- The branching and the hit normalisation are in `lib/search/query.ts` with 14 tests, since that is the whole of the merge and none of it was covered. Confirmed each can fail: a naive `{...raw, ..._formatted}` and an untrimmed query each break three of them.
- **Fixed in passing**: Meilisearch stringifies every value inside `_formatted`, so `imported_from_kahoot` arrived as the string `"true"` and the card's `=== true` test never matched — every Kahoot import read as "Made by" on the search page while reading "Imported by" on explore. Only `title` and `description` are taken from `_formatted` now; the rest of the hit keeps its real types.
- **Fixed in passing**: Explore called `response.json()` without checking the status, so a 500 from Meilisearch reached the template as an error object and threw on `.hits`. A failed search is now an empty page with a message.
- `search-card.svelte` rebuilt on the shadcn `Card`. It was `bg-white`/`dark:bg-slate-800` with `text-gray-800`/`text-gray-600`, and carried `my-20` on every card — which is where the huge vertical gaps came from, since the grid had no gap and each card paid for its own spacing. `min-w-0` on the link, because a grid item defaults to `min-width: auto` and a long unbroken title pushed the card out of its column. `highlightToHtml` and `lib/search/highlight.ts` are untouched.
- One Explore entry in the navbar, desktop and mobile, in place of the Explore/Search pair.


### Adding a question in the editor

- The rail's "Add question" button was the last child of the scrolling question list, so on a quiz with more than a screenful of questions it scrolled out of reach — you had to scroll to the bottom of the list before you could add anything. It is now a pinned footer of the rail, outside the scroll container.
- Added a second add control at the end of the canvas column, inside the reading measure, where a document editor puts it. Both open the same picker; the rail keeps its own.
- `AddNewQuestionPopup` is now the shadcn `Dialog`. It was a hand-rolled overlay with a `document.body` keydown listener for Escape and a `target === currentTarget` check for the backdrop, and no focus trap or focus return — so tabbing out of it landed behind the overlay. The question types, their descriptions and `add_question` are unchanged. Its own close button is turned off because the generated label is hardcoded English; the translated one is kept.


### Hosting without an account

- `/admin`, the screen that runs a live game, no longer redirects to the login page. The account-free path was built end to end on the backend -- an anonymous user can create a quiz at `/create?anon=true` and the server will start a game for them -- but the one screen that hosts it bounced them, so the path dead-ended at the moment of use. The wall was not access control either: `register_as_admin` accepts any valid game pin + game id pair from anyone, signed in or not, which is what it has always done.
- The "Save results" button is hidden for an anonymous host. The backend writes the `GameResults` row with `user=NULL` and every read path in `routers/results.py` is user-scoped, so the saved row would be unreachable. The podium and the spreadsheet export both work without an account and are unchanged.
- The loader returns `signed_in` and the page renders from it, rather than reading the `signedIn` store -- the store is module-scope state mutated during SSR, so it is shared across concurrent requests under adapter-node and is not safe to base this on.


### UI foundations

- The `brown.svelte` and `gray.svelte` button wrappers now forward `class`, `variant` and `size`, and `gray` gained the `label` prop `brown` already had. They hardcoded `w-full` and forwarded nothing, so a destructive button, or an accessible name on an icon-only button, was unreachable without abandoning the wrappers. `w-full` is still the default and is merged with `cn()`, so all ~30 existing call sites are untouched.
- Added the shadcn `dialog` and `collapsible` components. Four surfaces hand-roll an overlay with their own Escape, backdrop and focus behaviour; these land first so each can be converted on its own.
- The shadcn CLI's `-o` flag also rewrote `ui/button` and bumped the pinned `@lucide/svelte` from 1.42.0 to 1.46.0. Both were reverted -- the rewrite had dropped the `fq-touch-target relative` minimum-touch-target utility from the button base, which matters on the player's phone.

### Auth hardening

- Rate-limited every endpoint that checks a credential, keyed on something the caller cannot forge. `/login/step` now buckets on the account being guessed at, `/login/start` and registration on the address, and `PUT /users/password/update` on the account -- all of them previously had a per-IP bucket or none. The per-IP bucket became advisory the moment `TRUSTED_PROXY_HOPS` went above 1: the address it keys on comes from a header anyone can forge by reaching the backend directly, which is publicly reachable. Per-account and per-address buckets are not forgeable.
- Added a limit to `GET /users/verify/{key}`, which was unauthenticated and unthrottled. The key is 128 bits of `os.urandom` so this is defence in depth, not a hole being closed.
- `PUT /users/password/update` returns 400 rather than 500 for an account with no password, matching the delete endpoint.
- Mail sends now retry transient failures twice before giving up, and never retry permanent ones. There is no queue behind the sender, so a relay that blipped for a second cost somebody their confirmation link outright -- while the endpoint reported success, because it swallows send failures by design to avoid leaking which addresses exist. A 4xx from a relay is "not now" and a 5xx is "not ever": retrying a 550 for an unverified sending domain just delays the same failure three times over.
- Replaced "the account with the oldest `created_at`" as the definition of the instance admin with an explicit `users.is_admin` flag (migration `b5e91c7a2d38`). The old rule silently promoted the next-oldest account whenever the admin deleted theirs, which account deletion in the UI makes a thing a person can do by accident. The migration sets the flag on exactly the account the old rule was already pointing at, so the role did not change hands.
- Game results survive the host deleting their account mid-game. `game_results.user` is a foreign key, so saving results for a host who is no longer there failed the whole save at podium time and lost the game; the column is nullable and an ownerless row is worth more than none. The save is also wrapped now -- a missing history entry should not take the podium down.

### Account settings

- Added an unverified-address banner with a resend button. The page fetched `verified` and never rendered it, so someone whose confirmation mail was lost had no way to learn that from the one page about their account.
- The delete dialog now says how many quizzes are about to go with the account.

### Account deletion

- Added a delete-account card to `/account/settings`, confirmed with the password in an `AlertDialog`. `DELETE /api/v1/users/me` had existed since upstream with nothing in the app calling it, while the terms and the privacy policy both told people they could delete their account in settings.
- Gave `rating.user`, `rating.quiz` and `controller.user` `ON DELETE CASCADE` (migration `c3f8a1d47b62`). They were the three foreign keys `2ed6823c69b2` missed, so a single rating blocked account deletion partway through -- the quiz delete failed on `rating.quiz`, or the user delete failed on `rating.user` one step later, after the account's sessions and every one of its quizzes were already gone and committed. This also fixes `delete_quiz`, which 500'd on any quiz somebody had rated.
- Stopped the delete handler re-reading the user from the database. `get_current_user` resolves through the Redis cache, so a double submit authenticated a user whose row was already gone; the re-read then yielded `None` and `Quiz.objects.filter(user_id=None).delete()` is not "no quizzes", it is every anonymous quiz in the database.
- Deleting an account now clears its Redis cache entry, revokes its access token, drops its API-key cache entries and clears all four cookies. None of that happened, so a deleted account kept authenticating for up to 24 hours and the browser still believed it was signed in.
- Wrapped the deletion in a transaction, and moved the Meilisearch removal after the commit. It ran before a delete that could fail, which left quizzes present in the database and missing from search.
- Deleting an account now deletes its uploads. `storage_items` is `ON DELETE SET NULL` and nothing removed the blobs, so files outlived the account and the privacy policy's "takes your quizzes and uploads with it" was not true.
- Rate-limited `DELETE /users/me` to 5 an hour per account. It was an unthrottled password check, and each attempt costs a deliberately expensive argon2 verify.
- `DELETE /users/me` returns 400 rather than 500 for an account with no password. OAuth accounts are created without one, and `verify_password(x, None)` raises.
- Replaced the two `alert()` calls left in the settings password form with an inline message, and gave the login page a notice for a completed deletion or password change.

### Deployment

- Correction: an earlier entry in this section claimed `pnpm ci` in `frontend/Dockerfile` was not a pnpm command and broke the frontend image build. That was wrong -- `pnpm ci` is a real command, equivalent to a strict `install --frozen-lockfile`, and the frontend image had been building fine all along. The Dockerfile is unchanged.
- Set `COMPOSE_FILE` in the deployment `.env` so a bare `docker compose` picks up `docker-compose.neon.yml`. Without it the stack comes up pointing at the empty `db` container instead of Neon.
- Disclosed Resend in the privacy policy. It is the relay for confirmation and reset mail, and the page previously named the optional captcha as the only third party.

### Editor

- Replaced the question-reorder mode with drag and drop. Reordering was a toolbar toggle that laid two invisible half-card hit areas over every question, each containing an `<svg>` with no size class -- so it stretched to fill its grid cell and turning reorder mode on painted a pair of chevrons the size of the card over the content you were trying to reorder. Each question now has a grip: drag it with a pointer, or focus it and use the arrow keys. The hit areas were `role="button"` divs with no `tabindex`, so the old control could not be reached by keyboard at all; the grip is a real button, which is the single-pointer alternative WCAG 2.5.7 asks for.
- Reordering now moves rather than swaps. Dragging question 1 to the end used to trade it with the last one, scrambling everything in between.
- The selection follows the question that moved. Both reorder paths now share `moveItem` and `selectionAfterMove` in `lib/editor/reorder.ts`, with a property test asserting the selected index still points at the same question after every possible move.
- Added the theme switch to the editor header. It lived inside `navbar.svelte` as four near-identical copies, and the editor hides the navbar -- so the one screen people sit in longest had no way to change theme. It is now one `theme-toggle.svelte` used in both places, and switching toggles the class the boot script in `app.html` already looks for instead of calling `window.location.reload()`, which in the editor meant a round trip through the unsaved-changes prompt to change a colour.

### Emails

- Fixed the registration confirmation email's subject: "Confirm your frogQuiz address" read as confirming an email address, when the link actually confirms the account.

### i18n

- Fixed every plural in the app. The locale file uses i18next's v3 `_plural` suffix, but `i18n-service.ts` initialises i18next 25 with `compatibilityJSON: 'v4'`, where counted lookups resolve to `_one` and `_other`. All fifteen were silently falling back to the singular, so the app said "3 question", "2 player", "5 point". Renamed to the v4 spelling, with the bare keys kept for the uncounted uses.

### Local development

- Added `STORAGE_BACKEND`/`STORAGE_PATH` to `.env.example`. `docker-compose.yml` hardcodes `STORAGE_BACKEND: "local"` for the container, but `storage_backend` has no default in `config.py`, so running the backend directly with `pipenv run uvicorn` per the README's own Development section crashed on startup with a validation error unless `.env` set it by hand.

### Registration and recovery: edge cases

- Addresses are stored case-folded, and looked up case-insensitively. `Foo@x.com` and `foo@x.com` were two accounts, and only one of them was reachable by the reset and resend lookups -- so the other got the same neutral "a link is on its way" as everyone else and no mail, with nothing to distinguish the two outcomes. Pre-existing rows are still matched by a second exact-case query.
- `/users/reset-password` bounds the new password to 8-100 characters. Registration and `/password/update` both did; reset, the one password-setting route reachable without knowing the old password, took a one-character replacement.
- A spent or superseded confirmation link redirects to the login page with an explanation instead of rendering a raw 404 JSON body in the browser. Clicking the same link twice, or the older of two mails after a resend, are the two commonest ways to land there.
- Only one password-reset link is live per account at a time. Each request used to leave every earlier token valid for its full hour.
- A registration that loses the race to the unique constraint gets the same 409 as any other duplicate, not a 500. The existence check and the insert are not atomic, so a double-click could hit it.
- Rate limits on `/forgot-password` and `/resend-verification` are now applied per recipient address as well as per source IP. Per-IP alone is the wrong control for inbox flooding, and it collapses entirely behind a proxy that presents one address for every visitor.
- Added `TRUSTED_PROXY_HOPS` (default 1, unchanged behaviour). `client_ip` reads the last entry of `X-Forwarded-For`, which is correct behind the bundled Caddy alone and wrong behind Netlify-in-front-of-Caddy, where it is Netlify's egress address and identical for everyone -- making `/forgot-password`'s five an hour five for the entire user base. Documented in `DEPLOY.md`, including what raising it gives up.
- Rebuilt the login password step on the same Card primitives as the first step. It rendered a bare `<form>` with no header and no `Card.Content`, so the card opened straight onto a `Password` label flush to the edge -- no wordmark, no indication of which account was signing in, and no way back to correct a mistyped address. It now shows the address with a **Change** action, and the recovery hint sits as one quiet muted line under the button instead of inside the error, which had turned one fact into four lines of red.
- Replaced the login form's `alert('Wrong credentials')` and `alert("This shouldn't happen")` with inline errors, and gave every other status a message: a rate-limited or failed login previously produced no feedback at all, the spinner just stopped.
- Added `/account/resend-verification`, and pointed the login error and registration's "already taken" case at it. An account that has not confirmed its address is refused at login with exactly the same response as a wrong password -- deliberately, so the endpoint cannot be used to test which addresses are registered -- which left the one person it locks out with no way to find out why. The way out is now offered on every failure, which keeps the response uniform.
- Registration handles 423 (registration disabled), which fell through to the generic "something went wrong".
- The login page's confirmation badge sat beside the card rather than above it: it was a flex sibling of the card in a row.

- Replaced the editor's two `alert()` calls. `getEditID` showed a bare "Error!" on any non-200 from `/editor/start` and then resolved anyway, so the editor rendered behind the dialog as though nothing had failed -- which is what made the anonymous-quiz path unreadable at `/create?anon=true`: a native dialog with no status and no reason, over a form that looked fine. It now throws, and the `{#await}` block shows the status and the server's own detail with retry and home actions. A failed save gets the same treatment inline in the header, next to the validation warning.
- Made mail configuration optional instead of mandatory-but-ignored. `MAIL_ADDRESS`, `MAIL_PASSWORD`, `MAIL_USERNAME`, `MAIL_SERVER` and `MAIL_PORT` had no defaults, so the app refused to start without them, while `docker-compose.yml` hardcoded `SKIP_EMAIL_VERIFICATION: "True"` -- every deployment therefore demanded a full mail config and then never sent a confirmation with it. The settings now default to empty, `SKIP_EMAIL_VERIFICATION` reads from the environment, and the app logs a warning at startup when no relay is configured rather than failing silently later.
- Added `MAIL_SECURITY` (`starttls`, `ssl`, `none`) and `MAIL_FROM_NAME`. STARTTLS on 587 was hardcoded, which ruled out implicit TLS on 465 and a local relay that takes no credentials; `AUTH` is now skipped when no username and password are set. The TLS context is `ssl.create_default_context()` rather than a bare `SSLContext(PROTOCOL_TLS)`, which did not verify the server's certificate.
- Emails now carry a real `text/plain` alternative and a `Message-ID`. `MIMEMultipart("alternative")` promised two representations and only ever attached the HTML, which is a spam-filter signal and leaves plain-text clients with an empty message.
- Added `POST /api/v1/users/resend-verification`, and a "send it again" action on the registration result. There was no way to recover a lost or filtered confirmation email: the address stayed unverified and signing up again returned 409 forever.
- `/forgot-password` no longer skips unverified accounts. Anyone who registered while mail was down could neither verify nor reset, which is a dead end with no way out but the database. Following the emailed link proves control of the mailbox, so `/reset-password` now marks the account verified when it succeeds.
- `/forgot-password` no longer 500s when the send fails, and returns one message for every outcome. A 500 only reachable for a real address answers exactly the question the neutral response exists to avoid.
- Rebuilt `/account/reset-password` and `/account/password-reset` on the same Card primitives as login and register. Between them they had five `alert()` calls, one of which said "user not found!" -- an account-enumeration oracle, and a lie besides, since the API has never returned 404 there. Expired and already-used links now say so and offer a new one, and a link arriving without a token says that before anyone types a password twice.
- Rebuilt both transactional emails on one shared `base.jinja2` layout, so they read as the same product as the app instead of two unrelated messages. They now use Inter and the app's own palette and radii -- `--background`, `--foreground`, `--muted-foreground`, `--border` and `--primary`, converted out of oklch, which no mail client understands -- with the navbar's mark-then-wordmark at the top. What was there was upstream's: a `#348eda` blue cell behind a green button with a black hairline, a reset mail whose preview text read "Let's confirm your email address", and no visible URL for clients that block the button. Inter loads in Apple Mail, iOS Mail and Outlook for Mac; Gmail blocks web fonts, so every rule ends in a real system stack and the layout was checked with the font unavailable.
- Gave each email a hand-written `text/plain` template instead of deriving one by stripping tags out of the HTML. The strip-tags approach would have put the `<style>` block's CSS into the plain-text part as prose.
- Documented mail setup in `DEPLOY.md`, including the two things that actually go wrong: a `MAIL_ADDRESS` the relay will not send for, and `SKIP_EMAIL_VERIFICATION` masking the fact that no relay is configured at all.

- Fixed registration giving no feedback at all. `responseData` was assigned on every branch of the submit handler -- success, 409, 400, error -- and rendered nowhere, so clicking Register did nothing visible whether the account was created or not. My own regression from rebuilding that page on the new primitives: I screenshotted the empty form and never submitted it. The result is now shown inline, with a distinct message per outcome, and 429 is handled rather than falling through to the generic case (registration is limited to 10/hour/IP, so a few retries silently earned a rate limit).
- Fixed a failed verification email locking someone out of their address permanently. `create_user` saved the row and _then_ sent the email, with no error handling on either the send or the save. An unreachable or misconfigured mail server meant a 500 with an unverified account left behind; the next attempt hit 409 "user already exists", and there is no resend-verification endpoint to recover through. The send is now guarded and the row is deleted if it fails, so retrying works, and the caller gets a 502 that says nothing was saved.
- Made mail sending asynchronous. `_sendMail` was blocking `smtplib` called straight from async request handlers, so a slow mail server stalled the event loop for everything else, live games included. It now runs in a thread with a 15 second timeout, and the SMTP connection is closed on every path -- `quit()` was never called, so a server that accepted the connection and then rejected the login leaked it.
- Rewrote the privacy policy, which described a different company's infrastructure. It said user data sits "on the developers server, by Netcup, in Germany" -- that is upstream's hosting, not ours; the frontend is on Netlify and everything else on a server we run. Data location is a material disclosure under GDPR, so this was not cosmetic. It also named Google reCAPTCHA as the captcha when the instance supports hCaptcha or reCAPTCHA and neither is configured by default, gave "a very long time" as an IP retention period, and listed none of Redis, Meilisearch or object storage despite personal data sitting in all three. It now says what is stored, where, and for how long, per row.
- Rewrote the terms of service, which granted us rights we do not want and should not claim. It read "The admin is allowed to publish **ANY** data provided by the user" and "may publish any data provided by the user anywhere and share it with anyone" -- written by upstream's author, in the first person, for a hobby project, and flatly contradicting the privacy policy alongside it. It also bound users to German law and described frogQuiz as a platform for sharing educational content. The new text says what an internal tool can honestly say: provided as-is, no uptime guarantee, we remove rule-breaking content, we do not publish or sell yours.
- Removed every external image from the README: five shields.io badges at the top, plus the Ko-fi button and Liberapay goal badge in Credits. Seven third-party requests fired on every view of the page, each one handing shields.io or ko-fi.com the visitor's IP and referrer to render a picture of a number. The badges were also wrong: `CONTRIBUTORS` read 93, which is upstream's contributor count inherited through the fork, and `TESTS` read FAILING. The Ko-fi and Liberapay links stay in Credits as plain text links, which is the attribution without the beacon.
- Removed `.github/FUNDING.yml`. It listed `ko_fi: mawoka`, `liberapay: Mawoka` and `github: mawoka-myblock`, which put a **Sponsor** button on this repository routing donations to upstream. Anyone clicking Sponsor on frogQuiz was funding a different project without being told. The credit to Marlon W stays in the README, where the surrounding sentence makes clear whose project is being supported.
- Fixed two issue templates that GitHub could not parse. `Feature_request.md` and `Repo_architecture_changes.md` had their SPDX comment block _above_ the YAML frontmatter, and frontmatter has to start on line 1 -- so `name:` and `about:` never registered and both templates rendered as raw text with visible `---` delimiters. The feature-request template also asked contributors to "Describe the bug".
- Pointed the pull-request template's contributing link at our `CONTRIBUTING.md` instead of upstream's.
- Removed `.github/codecov.yml`. No workflow references codecov and nothing uploads coverage, so it was configuration for a service this repository does not use.
- Replaced `logo.png`, the image at the top of the README. It was still upstream's: "CQ" in ClassQuiz's green-and-brown chevrons, sitting directly under the frogQuiz heading. Same defect as the favicon and the Open Graph card, missed because it lives at the repository root rather than in `frontend/static`. Regenerated from the mark the app uses, and its SPDX sidecar now credits frogQuiz rather than carrying upstream's copyright on an image they did not make.
- Fixed the README advertising the project two ways at once. The header block still said "The open-source quiz-platform!" while the About section two screens below gave the real line, which is the same split the app itself had between `app.html` and `en.json`.
- Dropped Mapbox from the README's third-party list. It is named as an optional dependency and appears nowhere in the source.
- Documented the frontend test command. The Tests section covered `run_tests.sh` for the backend and said nothing about the 57 vitest tests, which need no services running.

- Added `BACKLOG.md`: a Kahoot!/Mentimeter feature and journey comparison against FrogQuiz's current capabilities, with a prioritized MVP2 backlog (word cloud, rating/scale questions, anonymous session mode, live Q&A/upvoting, moderation, mixed content+interactive session flow).
- Fixed a latent test-harness bug that surfaced as soon as a second `TestClient` test module existed: the async Redis client in `frogquiz/config.py` is a process-wide global, but the `test_client` fixture is module-scoped and each module runs on its own event loop, so the second module's first Redis command picked up a pooled connection bound to the first module's already-closed loop ("got Future attached to a different loop"). The fixture now resets the connection pool before building each client. Postgres was never affected — the app lifespan connects and disconnects it per module; nothing had ever reset Redis.
- Fixed optional authentication for fully anonymous requests and cleaned up the anonymous quiz test user.
- Added anonymous quiz creation and hosting: a "Create a quiz without an account" link on the homepage lets anyone build and host a quiz (share the pin, play it) without signing up. Ownership is proven by a random secret minted at creation and kept in the browser's `localStorage`, never a login. Anonymous quizzes are always private (never public/searchable), expire 30 days after creation (a daily cleanup job sweeps them and their images), and a signed-in user who still holds the secret can later "claim" one onto their account from its view page. New `POST /api/v1/quiz/claim/{quiz_id}` endpoint; `/editor/start`, `/editor/finish` and `/quiz/start/{quiz_id}` now accept an optional `X-Anon-Secret` header in place of a login. `Quiz.user_id`, `PlayGame.user_id` and `GameResults.user` are now nullable to represent an anonymous owner; fixed the several places (meilisearch indexing, the public quiz view, the live-game lobby cleanup) that assumed a quiz always has an owning user.
- Fixed the "remember me" auto-refresh path issuing its renewed login cookie without the `Secure` flag, unlike every other cookie-setting call site.
- Closed a gap where a revoked/logged-out access token still passed `check_token` and `get_current_user_optional`, which skipped the denylist check the other auth dependencies use.
- Added rate limiting to `/forgot-password` (5/hour/IP) — it was the only auth endpoint without one, so it could be used to spam a target's inbox or hammer the database.
- Password-reset tokens are now atomically read-and-deleted from Redis (GETDEL) instead of only expiring after their 1-hour TTL, closing both a replay window and a race where two concurrent requests with the same token could both succeed.
- Backup codes are now hashed at rest (like remember-me session keys already were) instead of stored in plaintext, compared with a constant-time check, and rejected outright (instead of throwing) if a webauthn-shaped dict payload is posted to the backup-code login step. A migration rehashes every existing value in place, so already-issued backup codes keep working.
- Fixed the client-IP rate-limit key taking the first (attacker-supplied) entry in `X-Forwarded-For` instead of the last one Caddy itself appends — the rate limiter was trivially bypassable behind the bundled reverse proxy. Reused the same fix for the IP address recorded on login sessions.
- Fixed `check_captcha()` calling a nonexistent `.model_dump_json()` method on the aiohttp response instead of `.json()` — dormant since hCaptcha/reCAPTCHA keys are unset by default, but would have thrown instead of validating if either were ever configured.

- Rewrote `docs/attribution`, which credited nine named people for contributing to and translating frogQuiz. They contributed to ClassQuiz. The page was upstream's contributor list run through the same global ClassQuiz→frogQuiz find-replace as everything else, so it turned their work into a claim about this project; deleting the locales made it worse, because it then thanked them for translations this build no longer contains. It now says what is true - frogQuiz is a fork, these people built the thing it is a fork of, their translations live upstream, and the credit stands either way.
- Deleted `frontend/src/lib/landing/testimonials.svelte`. Nothing imported it, but what was in it is worse than dead code: a real named person, a real tweet URL, and a quote whose text had been find-replaced so that an endorsement of ClassQuiz read as an endorsement of frogQuiz. One `import` away from rendering.
- Fixed two docs pages telling you to `git clone mawoka-myblock/ClassQuiz`, so anyone following either the self-hosting guide or the development setup installed different software than the page went on to describe. The OAuth error page also sent frogQuiz users to file bugs on upstream's issue tracker.
- Replaced all eight docs page descriptions. Every one carried upstream's "the open-source quiz-application", and two of them described a different page entirely - the privacy policy introduced itself as the self-hosting guide, and the develop page as the Kahoot importer.
- Replaced the taglines. "Live quizzes for the room you are standing in" shipped alongside a second, different description - "an internal quiz tool for running interactive quizzes" - so the app advertised itself two ways at once, one faux-poetic and one tautological. Both are now "The free Kahoot alternative. Host interactive quizzes right from your browser", in `app.html`, the web manifest and `en.json` (where `og:description` and `twitter:description` read from), so the three finally agree. The Open Graph image had the old line baked in as pixels and is regenerated.
- Dropped to English only and deleted the other 33 locale files. 34 files, 14,266 lines, of which 23 were registered and 11 sat on disk loaded by nothing; new keys were only ever written in English, so every other locale resolved them through `fallbackLng` anyway. The live hazard was the detector rather than the staleness: `i18next-browser-languagedetector` read `navigator` and `Accept-Language` before anything else, so a browser configured for Tamil got a half-translated Tamil UI off a header nobody set deliberately, and the RTL branch flipped document direction on the same evidence. Removing the language bootstrap from the root layout also removes a hydration mismatch, since the server rendered `'en'` while the client read `localStorage`. The `$t()` indirection is kept deliberately - collapsing it means inlining several hundred call sites for no user-visible gain, and keeping it makes the cut cheap to reverse. Documented in `docs/mvp-scope.md`, and **open** pending Gonçalo, since it removes a feature that exists on master.
- Fixed `og:image` never resolving. The image had been regenerated and verified; the tag pointing at it had not. It resolved to the Vite asset path `/_app/immutable/assets/opengraph-home.HASH.jpg`, which is root-relative, and Open Graph requires an absolute URL - Slack, LinkedIn and Discord will not follow a relative one. So the card rendered without its image no matter how correct the image was. Both image tags are built from the request origin now, which also means a deploy preview advertises its own card rather than production's, so it can be checked before it ships. `og:image:width`, `height` and `alt` added.
- Deleted `opengraph-home.webp`, which was a PNG carrying a `.webp` extension and would have been served with a Content-Type contradicting its own bytes. `twitter:image` pointed at it. No encoder here produces real WebP and the 1200x630 JPEG is the same image, so both tags use the JPEG. `favicon.ico` had the identical defect and is now a real two-header ICO wrapping the PNG, which the format has permitted since Vista.
- Fixed the font never loading. Tailwind v4 inlines an `@import`'s text but leaves its relative `url(files/...)` references alone, so Vite never saw the `.woff2` files as dependencies and emitted none of them: seven `@font-face` rules, seven 404s, `document.fonts` reporting `error`. Every screen redesigned in this branch had been built, screenshotted and contrast-measured against whatever `sans-serif` aliases to - a different face on every operating system. Importing the stylesheet from the module graph routes it through Vite's own CSS pipeline, which rewrites the urls and emits the files; all seven subsets ship now and `document.fonts.check` passes. The stack behind Inter is a named system stack for the same reason: a swap period or a failed load should land somewhere known rather than on whatever the OS aliases.
- Rebuilt the results list. The table carried hardcoded `gray-300`/`gray-500` borders that ignore the theme tokens and had no scroll container, so a long quiz title pushed the whole page sideways on a phone; it sits in `fq-scroll-x` now. The empty state was a single centred sentence stating a fact the user could do nothing about - it names what would fill the page and links to the quizzes that would do it.

- Replaced the Open Graph card, which was still upstream's: it said "ClassQuiz", carried "By Mawoka" and his avatar, and showed screenshots of the old green app. That image is what renders whenever anyone shares a frogQuiz link in Slack, Teams or a browser preview, so every shared link was advertising a different product. The new card is generated from the same mark the app uses.
- Replaced the favicon and app icons, which were "CQ" set in upstream's green-and-brown chevrons - every browser tab, bookmark and phone home screen showed ClassQuiz's initials. Generated from `Wordmark.svelte`'s own geometry so the icon and the in-app lockup cannot drift apart.
- Filled in the empty meta. `site.webmanifest` had `"name": ""` and `"short_name": ""`, and `app.html` shipped `content=""` as its description, so any page without a head of its own had nothing for search or a link preview to quote. `theme-color` was a single `#ffffff` that stayed white behind a dark page, and `msapplication-TileColor` was upstream's `#00a300`; both follow the theme now.
- Fixed every avatar in the app rendering as a broken image. The three avatar endpoints set their Content-Type by appending to a `PlainTextResponse`, which leaves `text/plain` in place as a _second_ Content-Type header; browsers honour the first, so a perfectly valid SVG body arrived labelled as plain text. They return a `Response` with the media type now. This is why the settings page showed "Profile image of reviewer" as wrapped alt text and the avatar builder was a grid of broken-image icons.
- Rebuilt the account settings page. It was a `grid-cols-6` with the avatar pinned to a one-sixth column, which on a phone collapsed into a broken image with its alt text wrapping round the heading, a clipped "change avatar", and three password fields squeezed into a row. It is a single column of section cards now, with an initial-letter fallback for when the avatar cannot load.
- Rebuilt the import page, which forced two columns with a border divider onto a 390px screen so each method's prose wrapped every two or three words. Two cards that stack, a styled file picker instead of a raw "Choose File | No file chosen", and no red invalid ring on a field nobody has typed in yet.
- Rebuilt the avatar builder's layout: the preview was crushed into a one-sixth column behind a `border-r-4 border-black`, the Back and Finish buttons were jammed into the heading row, and the choices were a fixed four-column grid at every width. It also now shows which step of twelve you are on.
- Gave the quiz title field a visible box. It is a rich-text field, and with no content it rendered as a label over blank space - so a new quiz showed "A title is required" with nowhere visible to type. ckeditor takes the element over on init and replaces the styling set in the markup, so the affordance has to be set on its editable.
- Stopped the command-palette notice covering the page heading, and stopped showing it at all on touch devices. Telling someone holding a phone to press Ctrl+K is advice they cannot take.

- Rebuilt the register page on the same Card/Label/Input/Button primitives as the login page it sits directly beside and looked nothing like. What was there was entirely upstream: floating labels over `bg-white`/`dark:bg-gray-800`, gray rings that turned `sky-600` on focus - a fourth accent the design system does not have, and `CLAUDE.md` is explicit that adding one is what makes this look generic - an inlined spinner with hardcoded `fill-blue-800`, and a `gray-700` submit. The consent checkboxes had their labels as siblings rather than parents, so tapping the words did nothing.
- Swept the same upstream idioms out of the import, password-reset and reset-password pages: the floating-label inputs, the `gray-700` submit, and a `text-blue-500` link that measured 3.60:1 against AA's 4.5 and was a fourth accent besides.
- Rebuilt the sessions table in account settings. It was a bare `<table>` with `whitespace-nowrap` cells and no scroll container - 539px of horizontal overflow on a phone - and Delete was a bare `<button>` with no box, so its target was the 42x20 of its own text. `CLAUDE.md`'s own rule is that a table may be wider than the page only inside its own overflow container.
- Fixed every page reporting horizontal overflow on a phone, which turned out to be two separate paint-region problems rather than layout. A `filter` or `backdrop-filter` expands an element's painted area about three blur radii past its box, and that phantom paint counts toward `document.scrollWidth` even for a `position: fixed` layer with nothing visible out there: the ambient background (blur 56px) and the navbar (`backdrop-blur-xl`) each reported 654px on a 390px screen. And a wide table inside a correctly working `overflow-x: auto` wrapper still contributed its paint to the document. `clip-path: inset(0)` on the first two, `contain: paint` on the scroll container, all three documented in `app.css` - the tempting `overflow-x: hidden` on `body` would have hidden real overflow along with the phantom kind.
- Darkened `--destructive` from 0.577 to 0.52. It measured 4.01:1 against its own 10% tint, which is the ground the destructive button and every destructive label actually sit on. Measured as the browser paints it: compositing the alpha in sRGB rather than mixing in oklab is a real 0.19 difference, and a first attempt at 0.535 still measured 4.48:1. The test now composites the same way, so the guard matches what renders.

- Split the reorder control into two plain buttons, "Move left" and "Move right". A bordered group with a shared "Move" label glued to two icon buttons was neither one control nor two, and read as strange rather than as either. Each button now says what it does on its own.

- Made reordering on mobile actually work. Moving the arrows into the question toolbar and labelling them fixed the ambiguity but not the question: the control still sat below the strip, pointing at a list it was nowhere near. Holding a question in the strip now picks it up and dragging repositions it, which is the idiom a filmstrip already has on a phone and the only one where the control _is_ the thing being reordered. A press delay separates picking up from scrolling, so a swipe still scrolls the strip. The Move buttons stay as the single-pointer and keyboard alternative, which WCAG 2.5.7 requires and which is also the discoverable path for anyone who never tries the gesture. Verified by driving the gesture: a long press reports `aria-grabbed`, a drag reorders, a quick swipe does not.
- No instructional line under the strip. The lift, the shadow and the other chips fading back are the feedback; telling someone to "drag to move, release to place" is the app explaining itself to a person already doing it.

- Added a frontend test suite. There were none: the frontend CI job ran eslint and nothing else, so "CI passes" meant very little on that side of the repo. 49 tests under vitest, run in CI, covering the things with real invariants rather than the things that are easy to assert - the answer palette, question completeness, the theme tokens, and the multiple-answer wire format.
- Fixed a question titled with nothing but spaces counting as complete. Found by one of those tests. `yup.string().required()` counts `'   '` as three characters, so such a question showed no "needs attention" dot, saved without complaint, and went up on the projector blank. The same hole was in all three answer-text fields. The docstring on `isQuestionComplete` claimed this exact case had been fixed; it had standardised on the wrong answer.
- Corrected the answer palette's documentation, which claimed it "passes CVD separation". It does not, and now there is a test that says so. Simulated, the distances collapse: under deuteranopia coral and green differ by 4 of 255 and sky and violet by 9. Four hues at one lightness cannot be separated by a dichromat. The design is still accessible because colour is never the only channel - every tile carries a distinct shape, and the host screen carries the answer text - which is what WCAG 1.4.1 asks. The test asserts the limitation deliberately, so that removing the shapes shows up as a failure rather than as nothing.
- Fixed long answers being clipped in the editor with no wrap and no ellipsis, so an author could only ever see the first twenty-odd characters of what they had typed. A text input cannot wrap; it is an auto-growing textarea now, which also matches the play tile the canvas is supposed to be previewing. An answer with no spaces in it now breaks rather than running out of its tile, on the editor, the player and the host.
- Made the reorder control say what it does. Bare chevrons beside "Question 1 of 3" read as previous and next, which is navigation - the opposite of reordering. The group is bordered and labelled Move, with the long-tailed arrows that mean displacement rather than the chevrons used for stepping through.

- Fixed the question title in the editor being black on a dark background, all but invisible in dark mode. `ckeditor5.css` sets its own text colour as a near-black constant and knows nothing about the theme; it is handed the tokens now, along with the balloon toolbar, which was otherwise a white slab.

- Put the editor's question list back in the layout at every width, and removed the drawer that had briefly hidden it on small screens. The list is the editor's navigation and the only place the quiz's shape and order are visible, so putting it behind a tap takes away the thing you need while editing. At `lg` and up it is an aside that collapses to a slim strip rather than sliding out of the flex row; below `lg` it is a horizontal strip of chips under the header, scrolling on its own axis so it costs no canvas width. The selected chip carries its own reorder arrows, because a drag handle inside a horizontal scroller fights the scroll gesture on a touch screen, and because reordering behind a mode toggle was already the least discoverable thing in the editor.
- Sized the projector screens for a room rather than a laptop. The host's type was a breakpoint ladder - `text-5xl md:text-6xl` for the question, `text-2xl` for the answers - which stops growing at 768px, roughly where a projector starts. Four clamped-vw utilities in `app.css` now carry it: `fq-display`, `fq-answer`, `fq-meta` and `fq-pin`. The minimum keeps every screen readable in a small window while the host sets up; the maximum stops a 4K display turning one question into wallpaper. Having the sizes in one place is also what stops the host question screen and the podium drifting to different scales again, which is how they got there.
- Added `docs/redesign-status.md`: which surfaces have been redesigned and verified, which are in scope and untouched, and which are deliberately skipped and why. The information existed only in commit messages and chat.

- Made `run_tests.sh` flush Redis as part of bringing the environment up. Sessions, login challenges and the token denylist live in Redis rather than Postgres, so dropping the database volume without clearing Redis left those keys behind and the suite failed from `test_password_update` onward with a cascade of 401s that reads exactly like broken auth code - 40 spurious failures from a warm cache. CI never hit it because `compose down --volumes` takes Redis with it; running the suite twice in a row locally does. Recorded in `CLAUDE.md` alongside the existing order-dependence warning.
- Fixed the player's waiting screen showing nothing but the quiz title after they joined: no confirmation, no sign of their own nickname, no indication anything was coming. Same failure as the blank screen after answering - there is no way to tell the app from a dead connection. It now names them, says the host is the one holding things up, and gives the title and description a real type hierarchy. It also carried both recurring layout bugs, `w-screen` and `h-screen`.
- Scaled the podium to the viewport. Fixed pixel heights made it a small object adrift in the middle of a projector screen with a third of the display empty below it, and 192 against 144 against 112 does not read as a rank order from the back of a room.
- Consolidated the two buttons on the host's final-results screen. They were separate fixed divs at `top-14` and `top-[6.5rem]`, each wrapped in a `w-fit` that fought `GrayButton`'s own `w-full`, so the pair rendered as two misaligned pills of different widths placed with magic numbers. The tick shown once results are saved was a hand-inlined Heroicon; it is the Lucide one now, with the label kept for screen readers.
- Strengthened the podium's floor, which at `border-b-2 border-border` did not register as a floor at projector distance - the blocks read as clipped off rather than stood on something.

- Documented the MVP scope cut in `docs/mvp-scope.md`: every question type that was taken out of the picker and why, the flags behind TOTP, QuizTivity and the box controller, what happens to content created before each cut, how to turn any of it back on, and the decisions still open. `CLAUDE.md` and `README.md` now point at it, because until now the reasoning existed only in commit messages and a pull-request description.
- Gave the editor canvas a measure. Content stretched to whatever the panel was, so the settings form ran to 900px of label and field with a lake of dead space between them. Capped and centred at `max-w-2xl`, modelled on the editor in the Noordhoff RFP work.
- Made the editor usable on a phone. The question rail was a fixed `w-72` column at every width, which leaves about 118px of canvas on a 390px screen; it is an off-canvas drawer below `lg` now, opened from the header and dismissed by picking a question, tapping the scrim, or its own close button. It also had to become opaque - `bg-muted/30` let the canvas show straight through it - and the reorder button's `w-full` was overflowing the rail header and pushing the close button outside the rail entirely.
- Fixed the editor's answer tiles bursting out of their grid cell on a phone: 367px of tile in a 308px column, which clipped the mark-correct button off the right edge. A grid item defaults to `min-width: auto` and refuses to shrink below its content's intrinsic width, and a bare `<input>` reports about twenty characters. The `min-w-0` belonged on the tile, which is the grid item, not on the input inside it.
- Replaced `h-screen` with `h-dvh` in the editor. `100vh` counts browser chrome that is not there on a phone, which put the toolbar below the fold.
- Rebuilt the "Add Media" control, the last un-migrated upstream button: its label was set in italic, there was no gap between it and its icon so the two collided, it carried `pt-10` of hardcoded dead space, an arbitrary `w-1/2`, a raw inlined Heroicon path, and `gray-500`/`gray-300` borders that ignore the theme. Its modal was `w-screen` - 100vw, which includes the scrollbar - with three `w-1/3` panels unusable at phone width.
- Fixed the host's question screen sitting flush against the top of the projector with the bottom half of the screen empty. It was the only game surface not wrapped in `fq-stage`, so it had no vertical centring and no padding, and the fixed controls bar and timer rule were drawn straight across the question title.
- Fixed the host's control bar, a two-column grid whose button cell asked for `col-start-3` - a column that does not exist - so the one control the host uses during a game ended up wherever the browser decided to put it. Its `admin-button` was also a hardcoded `gray-700` rectangle inherited from upstream, which read as a debug button beside the redesigned screens and ignored the theme; it is the shadcn primary treatment built from tokens now. The timer rule's offset was `mt-10` against what is now an `h-12` bar, so it cut across the bar's bottom edge.
- Fixed the per-question results reading zero for every option on a multiple-answer question. A CHECK player submits the indices of everything they ticked, concatenated, so a submission looks like `"02"`; the results component matched submissions against answer text, which never matches. It counts a submission once per option it names now, and the total underneath counts people rather than ticks, because on CHECK the per-option counts overlap.
- Fixed the CHECK submit button accepting an empty answer: ticking an option and then unticking it left an empty string behind, and an empty string is a value, so the button went live with nothing selected.
- Brought the CHECK answer tiles up to the redesign. They were still the pre-redesign ones: hardcoded black borders, the old bitmap icons, opacity as the only feedback. They use the shared palette, `AnswerShape` and the same pressable treatment as the single-answer tiles now, with a persistent ring on ticked options since a choice here is something you can undo and has to stay legible for the whole round.
- Wrote down the CHECK scoring rule, which was implemented and documented nowhere: it is all or nothing, with a test pinning the partial, over-selected and empty cases.
- Stopped the Kahoot importer overriding the answer palette. It stamped a hardcoded four-colour list - the old green and brown one - onto every imported answer, so an imported quiz kept looking like the pre-redesign app however the design changed, and indexing that list by choice position raised `IndexError` on any question with more than four choices. It also now states `type=ABCD` rather than relying on the model default, with a test, because it was worth proving the importer is not a back door to the question types the MVP cut. And it skips Kahoot surveys and polls, which have choices but mark none correct and so imported as rounds nobody can score.
- Gated only the TOTP _setup_ endpoints behind `ENABLE_TOTP`, not the whole 2FA router. The login flow still honours a secret that is already set, so switching the router off entirely would have left anyone who enabled TOTP before the cut stuck behind a factor they could no longer remove - a lockout of our own making. Reading the status and switching it off now work whatever the flag says; both already require the account password. A test covers the split.
- Made the two lint jobs actually run. `backend_lint` only triggered on `pull_request`, and work here has been merged straight to master, so it never ran on the commits that mattered. `frontend_lint` filtered on `"frontend/**/*.{ts,js,svelte}"`, and GitHub's path filters do not do brace expansion, so that pattern was matched literally and hit nothing: the workflow's entire run history is one manual dispatch and one push that happened to edit the workflow file itself.
- Cleared the six eslint errors that had accumulated on master while that job was dead - all dead code: an unused import in the navbar, a tippy factory whose tooltip was removed from the markup, two `performance.now()` readings nothing reads, and a deliberate no-op prop on the brown and gray buttons which is suppressed with its reason instead.
- Fixed `pnpm lint` and `pnpm format`, which passed `--plugin-search-dir`, removed in Prettier 3. The flag is ignored with a warning, `prettier-plugin-svelte` never loads, and the run dies on the first `.svelte` file with "No parser could be inferred". The plugin is declared in `.prettierrc` now, and the negative globs in both scripts were duplicating `.prettierignore`, which already lists all of them - and disagreeing with each other, so `format` would have rewritten `pnpm-lock.yaml` that `lint` never checked.
- Formatted the 37 frontend files that had drifted while that plugin was silently not loading. Mechanical, no behaviour change.
- Corrected stale claims in `CLAUDE.md` and `README.md`: the redesign status, the locale count (34, not 30), MinIO still listed as a development service after it was removed, and upstream's product copy describing frogQuiz as a tool for schoolteachers. Added a section recording the layout mistakes this codebase makes repeatedly and the responsive baseline to check a screen against.

- Added an auth dependency to `DELETE /api/v1/quiztivity/{uuid}`, which had none at all. Anyone who knew or guessed a QuizTivity's UUID could delete it, including someone else's; the endpoint now requires a logged-in user and only matches rows that user owns, exactly as the neighbouring `PUT` already did. A regression test covers the unauthenticated call and asserts the object survives it.
- Scoped `DELETE /api/v1/users/api_keys` to the calling user. It looked the key up by value alone, so any authenticated user could revoke any other user's API key if they ever saw it.
- Put QuizTivity and the box-controller hardware endpoints behind `ENABLE_QUIZTIVITY` and `ENABLE_BOX_CONTROLLER`, both off by default. PR #5 removed their entry points from the UI but left the routers registered, so every endpoint stayed live and callable by anyone who typed the URL - obscurity rather than access control. They now return 404 and no longer appear in the OpenAPI schema. Moderation was left as it was: it is already gated on the `mods` allowlist, which is real authorisation.
- Added the matching frontend half in `hooks.server.ts`: `/quiztivity`, `/controller`, `/account/controllers` and `/account/settings/security` now 404 rather than rendering a page for a feature whose API is switched off.
- Cut TOTP and its backup codes behind `ENABLE_TOTP`, off by default. The 2FA router is no longer mounted, the security-settings page (which contained nothing else) is unreachable, and the "Use backup-code" button is gone from the login password step. The code is all still in the tree for the day company SSO makes a second factor worth having.
- Rebuilt the quiz editor around one idea: the canvas should be the room. The answer editor now renders the real game tiles - the same palette, the same triangle/diamond/circle/square shapes, the same order - so the author sees exactly what will go on the projector instead of a list of red and green pills that looked nothing like the result.
- Removed the per-answer colour picker. Slot colour is derived from the answer's position instead of stored, which keeps the four hues in order after an answer is deleted and matches what every play surface already did (`answer.color ?? default_colors[i]`). The palette was derived and validated for colour-vision separation; letting an author pick two near-identical hues by hand is the thing that work existed to prevent. Colours saved by older quizzes are still honoured.
- Moved the correct-answer marker off the tile background and onto an explicit control on the tile. Right and wrong were carried by a red or green fill, which fought with the tile's own identity colour and left the editor unable to show both at once.
- Gave the editor a real chrome: a header with a back link, the quiz title and Save; a per-question toolbar carrying time and single-versus-multiple-answer; and a question rail that numbers each question and flags the unfinished ones with a dot. The header now says how many questions still need attention instead of printing a raw yup validation path.
- Replaced the fake macOS window chrome - three coloured dots drawn at the top of both editor panels - with a row that says which question is open and holds its settings.
- Rebuilt the quiz-settings panel as a labelled form (title, description, cover image, visibility, background colour, background image) instead of an unlabelled stack with a three-swatch colour control in the middle of it.
- Cut the question types down to multiple-choice and check-choice. RANGE, TEXT, VOTING, ORDER and SLIDE can no longer be created: each one multiplies the editor, the play screen, the results screen and the scoring path, and none of them is what people run a live quiz for. True/false needs no type of its own - it is a multiple-choice question with two answers. Existing quizzes that already use a cut type still open and still play; only the "add question" list changed.
- Removed the "add slide" button, which was SLIDE's only entry point, and the dead modal at the bottom of the edit route whose open flag was never set.
- Fixed the player's screen going completely blank when the question timer ran out and they had not answered. The "Answer locked in" state added previously was gated on having submitted an answer, so anyone who ran out of time saw nothing at all - the worse case, because they cannot tell the app from a dead connection. There is now a "Time's up" state alongside it.
- Removed the `text-black dark:text-black` wrapper around the player's question screen, which forced black text on a dark background and made both the post-answer and time-up states nearly unreadable. The answer tiles set their own ink inline from the tile colour and never needed it.
- Fixed the host's per-question results running off the bottom of the screen. `admin.svelte` wrapped every host screen in an `fq-stage` - full viewport height plus padding - and each screen inside it is an `fq-stage` too, so the page was always taller than the viewport and the scoreboard only appeared if someone scrolled. Measured 245px of overflow before, 1px after. Two `<br>` tags used as spacers went with it.
- Fixed the dashboard overflowing horizontally by 338px. The five toolbar buttons sat in a four-column grid whose last cell held two buttons that could not shrink, so Settings hung off the right edge of every session.
- Stopped the editor arming the browser's "changes you may not have saved" prompt on mount, so opening a quiz and going straight back no longer asks whether you want to discard changes you never made. It now arms on the first real edit.
- Rebuilt the dashboard. It had no container, so the toolbar ran edge to edge and the copy sat flush against the viewport; quizzes were 20vh cards outlined in the old `#B07156` brown with six unlabelled icon buttons. It is now a contained list with Play as the one prominent action, a public/private badge and a question count, a search box that appears only once there are enough quizzes to need one, and an empty state that invites you to create or import rather than stating a fact.
- Replaced the last hand-inlined Heroicons in the dashboard, editor and login password step with Lucide icons, including two spinners drawn with a hardcoded `fill-black` that were invisible in dark mode.
- Flattened the inline rich-text editor, which rendered as two nested bordered boxes wherever it was used and carried its own dark-mode greys.
- Rebuilt the login password step on the shadcn Label, Input and Button, matching the first step. It also never set its `isSubmitting` flag, so the button showed no pending state and nothing stopped a second submit while the first was in flight.
- Committed the Vite dev proxy for `/api` and `/socket.io`. Without it the dev server cannot reach the backend at all, and every local run needed the same proxy hand-wired back in; it affects only `vite dev` and never the built app, which is served behind Caddy.
- Filled in the abuse-report and data-deletion contacts in the terms of service, `CONTACT.md` and `CONTRIBUTING.md` with francois.prevot@frog.co as an interim address. The GDPR deletion route pointed at a placeholder. Each site keeps a TODO for the team's shared channel.
- Corrected the project name to frogQuiz throughout, including the `SPDX-FileCopyrightText` lines we had added ourselves. Mawoka's copyright lines were not touched.
- Fixed `backend_lint`, which has been failing on master since 658249a: that commit left three blank lines between two functions in `frogquiz/auth.py` and a 135-character line in `frogquiz/oauth/authenticate_user.py`. Both are formatting-only fixes.
- Turned `ENABLE_QUIZTIVITY` on in `.env.ci` so the eleven QuizTivity tests keep covering that code while the feature is off by default, and so the flag itself is exercised.
- Removed the `minio` service from `docker-compose.dev.yml`. MinIO stopped publishing container images to Docker Hub and Quay.io and archived the community repository, so pulling `docker.io/minio/minio` fails — and because that pull aborts the whole `compose up`, the database never started either. That is what actually caused the PyTest workflow's 56 `ConnectionRefusedError` failures. Nothing in the test path used it: the CI environment runs `STORAGE_BACKEND=local`, and `test_minio` talks to `play.min.io` rather than a local container.
- Fixed the PyTest workflow racing Postgres. `run_tests.sh` waited a flat `sleep 2` after `docker compose up -d` before running migrations and the suite, but the container is up well before the server accepts connections. When the race was lost, every database-backed test failed with `ConnectionRefusedError` and nothing in the output said why. Postgres now has a `pg_isready` healthcheck like redis already had, the script polls for readiness instead of guessing, and a failed environment aborts with the compose status and database logs rather than 56 misleading test errors.
- Rebuilt the per-question results as one card instead of two unrelated stacked objects. It now leads with the question, then the answer distribution, then the standings - the order the room actually cares about.
- Replaced the answer-distribution chart. It drew vertical bars with labels rotated 45 degrees that collided and overprinted each other, bars that were not proportional, and no marking of the correct answer. It is now horizontal bars - which removes the need to rotate long answer text at all - in the answer's own colour, with the shape repeated beside the label so identity never rests on colour alone, and the correct row marked with a tick and a ring.
- Replaced the answer colours with a pastel palette derived from the frogConvert brand rainbow, so the two products read as one. The four hues (coral, sky, green, violet) were re-stepped in OKLCH to L=0.76 C=0.13 and checked with a palette validator rather than by eye: the first attempt paired amber with green at ΔE 8.6 for normal vision, which is genuinely hard to tell apart, so the hues were re-spaced to 80-110° and now measure ΔE 17.1 at worst, passing colour-vision separation and contrast on both surfaces.
- The palette now lives in one module. The same four hex values had been copy-pasted into six separate files, which is why there was no colour system to speak of.
- Built a real podium for the final results. The leaderboard was one `<p>` per player with a computed font size — literally "1: Froggo with 377 points" as body text, at the emotional peak of the product. It is now a three-place podium that builds from third to first, with the winner's block highlighted, confetti timed to their arrival, and ranks four and below as a clean list.
- Moved the host's result-export controls out of the podium composition; they were floating over it.
- Replaced the answer icons with the four classic simple shapes (triangle, diamond, circle, square), drawn inline so they take `currentColor` and keep contrast on any tile colour. The previous SVGs were heavy abstract blobs baked black.
- Rebuilt the host lobby. It was three unaligned columns with the player chips stranded bottom-left and a default-sized Start button; it is now one centred composition with the PIN as the largest element, the QR beside it, a real primary action and animated player chips. Kicking a player is now a labelled button rather than a click handler on a span.
- Rebuilt the host question screen: balanced question type, a thin timer rail instead of the full-width red block that duplicated the countdown ring, and answer tiles matching the player treatment. Answers now read row-major, in the same order players see them on their phones.
- Gave the question counter a legible pill. It was 14px of body text in the corner of a projector screen.
- Rebuilt the player answer tiles: rounded, with gloss and floor shading so they read as pressable, a staggered entrance, hover and press response, and a clear picked state where the chosen tile lifts and the others recede. The hard black borders are gone.
- Gave the answer buttons real accessible names. They previously announced as "Icon" because the shape image's alt text was the button's only content; they now announce the answer.
- **Filled the blank screen after answering.** Once every player had answered the timer stopped, the tiles unmounted and nothing replaced them, so the phone went empty with no confirmation the answer had registered. Added an "Answer locked in / waiting for everyone else" state, with the strings added to all 34 locale files.
- **Fixed the host screen crashing during every question.** `play/admin/question.svelte` iterated answers with `{#each ... as answer}` but referenced an index `i` four times inside the loop, throwing `ReferenceError: i is not defined` on render. The projector screen silently fell back to the quiz title, so nobody in the room could read the question or the answer options for the whole round. One missing index binding.
- Marked the answer shape images decorative (`alt=""`) so screen readers announce the answer text rather than "icon".
- Pinned `@lucide/svelte` to 1.42.0 and `bits-ui` to 2.19.0. The Docker build runs pnpm 11.6, which enforces a 24-hour minimum release age on lockfile entries; both packages had been published the day before and failed `ERR_PNPM_MINIMUM_RELEASE_AGE_VIOLATION`. Pinned exactly rather than with a caret, since a range would resolve straight back to the fresh release, and the policy itself was left alone — it is there to catch compromised packages that get yanked quickly.
- Added the ambient background layer (`lib/components/AmbientBackground.svelte`): the brand rainbow as small, heavily blurred smudges scattered towards the page edges, which is how frogConvert actually spends that palette. Mounted once in the root layout.
- Made `body` transparent so that layer is visible. `html` keeps the `--background` token, so the page ground is unchanged; a `body` background would have painted over any negative-z-index element.
- Fixed `backend_lint`, which has been failing on master since b478a50: making email sending synchronous left `BackgroundTasks` imported but unused in `frogquiz/routers/users/__init__.py`, and flake8 treats F401 as a build stopper.
- Removed Sentry entirely. The backend still imported `sentry_sdk`, initialised it whenever a DSN was configured, and ran an HTTP middleware that attached the full request (URL and headers) to every captured exception before shipping it. It was dormant only because no DSN happened to be set. Gone from `frogquiz/__init__.py`, the `sentry_dsn` setting, the `sentry-sdk` dependency, `VITE_SENTRY`, and the self-host docs.
- Corrected the privacy policy, which claimed frogQuiz used a GlitchTip instance for error logging and Plausible for usage data. Neither is true: there is now no analytics and nothing is reported to a third party.
- Replaced the Marck Script cursive wordmark with a proper lockup: a rainbow-gradient mark plus "frogQuiz" set in Inter (`lib/components/Wordmark.svelte`). The `.marck-script` class is kept for its 14 call sites but no longer loads a script face.
- Replaced every hand-inlined Heroicons SVG in the navbar and landing page with Lucide icons. Several had `stroke="#000000"` hardcoded and were invisible in dark mode.
- Rebuilt the front page around what people actually come to it for: entering a game PIN. The marketing sections ("1. Get a quiz", "2. Play the quiz", "Why frogQuiz?") were upstream's public-site pitch and are gone; the page went from 316 lines to 95.
- Removed the landing page's screenshots, which showed a ClassQuiz-era UI that no longer exists.
- Quietened the landing icon chips (they were saturated `bg-lime-500`/`bg-emerald-300` squares) and fixed the type hierarchy so large headings carry less weight, not more.
- Raised the base radius to 0.875rem and added breathing room and layered shadow depth.
- Fixed a stray vertical rule on the landing cards, left over from a two-column layout that had been collapsed to one.
- Fixed the home page having two `<title>` tags, and meta descriptions still pitching frogQuiz as "like KAHOOT!, but open-source".
- Documented in `CLAUDE.md` what a full removal of Explore or Search would actually involve, including the Meilisearch write paths in quiz create/edit/import. Nothing was removed — both are kept.
- Replaced the error pages with a branded shadcn card (status, plain-language message, Home / Try again). They previously rendered a cat meme fetched from `http.cat` on every error, which was both off-brand and a third-party request telling an outside service that our users had hit an error.
- Rewrote the landing page copy for an internal tool, and dropped three claims that are simply untrue for our deployment: "German Server" (hosted by netcup), "Community-driven" (funded by its community) and "Completely Cost Free" (no paid plans, donations appreciated).
- Fixed the registration form showing every field outlined in red on first load: the check was `$errors.field !== null`, and the pristine value is `undefined`, so the error styling was always on.
- Fixed the "Changes you made may not be saved" browser prompt firing on every navigation away from `/play`, even from an untouched join screen — it is now armed only once a player has actually joined a game.
- Removed the last live `plausible()` calls (game join, game start, hashcash) and the shim in `app.html` that was swallowing them. Plausible itself was removed in PR #5; the calls would otherwise throw against an undefined global.
- Fixed three wrong flags in the language picker: English showed 🇺🇲 (US Minor Outlying Islands), Hebrew showed 🇯🇵 (Japan) and Traditional Chinese showed 🇨🇳. Language names now use endonyms throughout.
- Pointed the shared brown/gray buttons at the shadcn Button, which moves 30 call sites off the hardcoded `#B07156` brown in one step without touching them.
- Moved the page ground onto the `--background` token, removing the hardcoded `#d6edc9` / `#4e6e58` greens from the root layout.
- Tokenised the footer, the language select and the game-PIN inputs, which were hardcoded to colours that were invisible in dark mode.
- Swapped the shadcn theme from green back to neutral zinc, so `--primary` is near-black rather than the brand green.
- Set up shadcn-svelte 1.6.1 as the redesign component system: added `frontend/components.json` (style `vega`, base colour `zinc`, theme `green`, Lucide icons, Inter), the `cn` helper at `$lib/utils.ts`, and the first components (button, input, label, card, badge, separator) under `$lib/components/ui/`.
- Applied the shadcn design tokens and canonical base layer to `app.css`, replacing the pale-green `#d6edc9` page ground with `--background`; the existing SPDX header, tippy imports, `@config` link and legacy `@utility` blocks were preserved.
- Rebuilt the login page on shadcn-svelte Card/Input/Label/Button as the reference page for the redesign, replacing the hand-rolled floating-label input with a real `Label` + `Input` pair.
- Fixed the horizontal scrollbar present on every page: the navbar and footer used `w-screen` (`100vw`), which includes the vertical scrollbar's width and so overflowed by ~15px.
- Migrated the navbar chrome off hardcoded colours (`bg-white/70`, `text-black`, `btn-nav`'s `text-gray-600`) onto theme tokens, so it no longer renders as a white bar with an invisible wordmark in dark mode.
- Pinned pnpm 10 for the frontend (the repo's lockfile is v9; pnpm 12 wanted to rewrite it).
- Fixed the light/dark theme toggle, which had silently done nothing since the Tailwind v4 upgrade: `tailwind.config.cjs` (holding `darkMode: 'class'`) was no longer being loaded, so all 319 `dark:` utilities compiled against the OS `prefers-color-scheme` setting instead of the `.dark` class the app actually toggles. Re-linked the config from `app.css` with `@config`.
- Fixed the brand green, lost in the same regression: `green-600` had reverted to stock Tailwind green instead of `#009444` across the 15 places it is used.
- Added a pre-paint theme script to `app.html` so dark mode no longer flashes light on load, now that the theme depends on a class set by JS rather than a media query.
- **Security:** added the missing authentication check to `POST /api/v1/editor/finish`. It had no auth dependency at all, so knowing the 32-bit `edit_id` was enough to write a quiz into its owner's account — reproduced against a live stack before the fix.
- **Security:** enforced the 8-character password minimum server-side on registration and password change. It had only ever existed in the register form, so the API accepted a one-character password.
- **Security:** logging out now actually ends the session. Token validation only checked signature and expiry, so a copied token stayed valid after logout; revoked tokens are now held in a Redis denylist for the remainder of their lifetime.
- **Security:** fixed a units bug that made "remember me" mint a token 60x longer-lived than a normal login (30 minutes became 30 hours).
- **Security:** auth cookies are now marked `Secure` on HTTPS deployments, derived from `ROOT_ADDRESS` so there is no extra setting to forget.
- **Security:** remember-me session keys are stored hashed rather than in plaintext, so a database read no longer hands over live sessions.
- **Security:** added Redis-backed rate limiting to login and registration, which previously had none. Controlled by `RATE_LIMIT_ENABLED` (on by default; off for test runs).
- Made an unreachable MeiliSearch non-fatal at startup. It previously aborted boot, so a search outage took the live game loop down with it.
- Fixed `CORS_ORIGINS` so the documented comma-separated form works. It raised before the validator ran, leaving only the JSON-list form functional — the setting the Netlify split-hosting depends on.
- Added `validate_email_deliverability` so deployments on internal-only mail domains can skip registration's live DNS/MX lookup. Default unchanged.
- Declared `databases` in the `Pipfile`; it is imported directly but only resolved via the lockfile.
- Wrapped raw SQL strings in two migrations in `sa.text()`, which SQLAlchemy 2.x requires — they would break on the next dependency refresh.
- Gave the dashboard's icon-only buttons accessible names, using existing translation keys. Five of eight buttons, including delete, were announced as unlabelled.
- Labelled the join screen's inputs and gave the PIN field autofocus and `autocomplete="one-time-code"`.
- Finished removing passkeys: setup was already gone, but the login path remained, so a passkey could be used to sign in while none could be registered.
- Removed a stray `console.log` shipping in the OAuth login block.
- Created `CLAUDE.md` with project scope, feature triage policy, licensing rules, and collaboration workflow.
- Created this changelog and wired automatic logging into `CLAUDE.md`.
- Fixed mobile nav GitHub link, which still pointed at the upstream ClassQuiz repo.
- Hid Ratings (like/dislike) from the public quiz view page.
- Hid the Moderation panel (route now 404s; backend untouched).
- Hid box-controller hardware pairing: removed its link from account settings, removed the "frogQuizControllers" toggle from the start-game popup (routes/backend untouched, now unreachable from the UI).
- Hid Quiztivity: removed "Create Quiztivity" from the command palette and stopped fetching/listing quiztivities on the dashboard (routes/backend untouched).
- Hid API keys management from account settings.
- Hid WebAuthn/passkeys: removed the security-key section from account security settings and the passkey option from the login method selector.
- Trimmed the docs index to only link pages relevant to kept features (Kahoot import, Features); privacy-policy/tos/self-host/roadmap/develop/attribution/pow are now unlinked but still reachable by direct URL.
- Documented that OAuth login buttons (Google/GitHub/custom OIDC) are intentionally left unconfigured in `docker-compose.yml`.
- **Removed** (not just hidden, for data-privacy reasons) the newsletter signup form on the homepage — it posted visitor emails/names to `newsletter.mawoka.eu`, the original maintainer's own service.
- Removed the Plausible analytics script and Sentry error-reporting call, both of which pointed at the original maintainer's own external infrastructure.
- Fixed `frontend/Dockerfile`'s `API_URL` default, which was `https://mawoka.eu` — a live risk if the image were ever run without an explicit override. Also removed a stale Mapbox comment and a commented-out Sentry DSN example pointing at the maintainer's own error tracker.
- Removed the quiz-report mailto link (pointed at the original maintainer's email) and the import-template download link (hosted on the original maintainer's blog subdomain) pending internal replacements.
- Replaced the transactional email footer's UTM-tracked link to the original maintainer's site with plain text.
- Updated `CONTACT.md`, `CONTRIBUTING.md`, and the ToS page's contact/abuse-report/data-deletion mentions to point at internal placeholders (marked with TODOs — need the team's actual contact channel).
- Added an "Upstream independence" principle to `CLAUDE.md` covering all of the above, going forward.
