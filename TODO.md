<!--
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

# TODO — live tracker

Where the work actually stands. [`MVP.md`](MVP.md) is the plan and holds the decisions;
this file is the running state, updated as things land.
Audit that produced most of it: [`docs/audit-2026-10-01.md`](docs/audit-2026-10-01.md).

**Branch:** `ccr-370df3e4-c44t1l` · **Suites:** 126 unit · 119 e2e · 147 backend (1 skipped)
· **Last full green run:** 2 Oct — e2e **119/119** in 8.9m, backend **147 passed**, unit 126 passed,
`flake8 .` 0, `eslint .` 0 errors, production build OK

---

## Done — 1 Oct

| # | What | Where |
| - | --- | --- |
| 1 | **Editor rebuilt as one column of question cards** (D7). Open card edits in place, the rest stay as question text plus answer chips; add between cards, duplicate, drag or arrow to reorder, delete behind a confirm; a new quiz shows two fields and "Add your first question"; True / False preset | `lib/editor/question-card.svelte`, `lib/editor.svelte`, `e2e/editor-column.e2e.ts` |
| 2 | **Editor no longer drops an edit** typed in the first half-second after it opens | `lib/editor.svelte`, regression test in `e2e/editor.e2e.ts` |
| 3 | **Hidden routes get the real 404** with the navbar and a Home button, instead of SvelteKit's bare fallback | `lib/hidden_routes.ts`, `hooks.ts`, `e2e/hidden.e2e.ts` |
| 4 | **Players are told whether they were right** — icon, word, points, total and place | `lib/play/results_kahoot.svelte`, `e2e/player-feedback.e2e.ts` |
| 5 | **Host results scale for a projector**; podium side buttons outlined; export anchor out of the a11y tree | `lib/play/admin/`, `routes/admin` |
| 6 | **Play is not offered on somebody else's unlisted quiz**, which the server refuses | `routes/view/[quiz_id]`, `e2e/account.e2e.ts` |
| 7 | **Join screen rebuilt** on the landing page's PIN card | `lib/play/join.svelte` |
| 8 | **Copy, nav and hygiene**: inverted Register link, Explore→Discover, "Forgot password?" off the register form, the empty My Quizzes banner, "This session?", the empty colour input, upstream's false landing copy and its dead component | several |
| 9 | **Docs match reality**: D7 closed with its deviation, D16 and D17 added, the six missing lines in, `CLAUDE.md` no longer claims `--primary` is green | `MVP.md`, `CLAUDE.md`, `docs/audit-2026-10-01.md` |
| 10 | **Podium**: builds up third → second → first, 1.4s apart, crown and confetti, nothing under reduced motion. Flat gold winner, 2nd and 3rd on theme surfaces — the medal gradients are gone | `lib/play/admin/final_results.svelte`, `e2e/podium.e2e.ts` |
| 11 | **`e2e/run.sh` runs on Linux and macOS** as well as Windows: finds Postgres wherever it lives, drops to the `postgres` user when run as root, uses the real `redis-server` when there is one, fetches the right Meilisearch build, and picks Edge or Chromium per platform | `e2e/run.sh`, `e2e/stop.sh`, `frontend/playwright.config.ts` |
| 12 | **Game surfaces fit a phone.** The podium's action panel covered the podium at 390px; it is a bottom row below `sm`. Lobby → question → results → podium asserted at phone width | `lib/play/admin/`, `routes/admin`, `e2e/podium.e2e.ts` |
| 13 | **Corners come off one scale.** Four sites rendered a 4px corner because a bare `rounded` resolves to Tailwind's own `--radius`, not ours; cards disagreed by 5.6px; the view page nested equal radii; the host's answer row drew itself two ways | `src/app.css`, 10 components, `src/lib/a11y/radius-scale.test.ts` |
| 14 | **One motion scale.** Fifteen ad-hoc durations and almost no easing became five durations and four curves, declared once in `app.css` and mirrored in `lib/motion.ts` for Svelte's JS transitions, which never see a CSS variable. Three bars animated `width`, which lays the page out every frame; they animate `transform` now. Reduced motion clamps the whole scale to 1ms | `src/app.css`, `lib/motion.ts`, `lib/a11y/motion.test.ts`, `e2e/motion.e2e.ts` |
| 15 | **Uploads have limits, and there is still no file manager.** There was no server-side size cap at all (`size = 0` went into storage, the only limit was Uppy's in the browser, and the endpoint takes anonymous uploads) — and the browser's cap was not applied either, because `restrictions` is an Uppy *Core* option and was passed to the Dashboard plugin. 5MB per image and 1GiB per account, enforced at Caddy, on `Content-Length`, and on the counted bytes; the quota counts the file in hand; `/raw` aborts mid-stream; `video/mp4` behind a flag | `frogquiz/config.py`, `routers/storage.py`, `frogquiz/__init__.py`, `Caddyfile*`, `lib/editor/uploader.svelte`, [`docs/uploads.md`](docs/uploads.md) |
| 16 | **A game survives someone closing their laptop.** There was no socket `disconnect` handler, so a closed tab stayed in the count "everyone answered" is measured against and the host sat through every full timer for the rest of the game. Disconnect drops the player from the count but keeps the rejoin key, so a backgrounded phone can still return; `rejoin_game` re-announces them, which it never did | `socket_server/__init__.py`, `e2e/disconnect.e2e.ts` |
| 17 | **A refused answer says so.** `question_not_active` had no listener anywhere, so an answer the server threw away still read "Answer locked in". Fixed with the listener leak beside it — the component is recreated per question and never released its subscription | `lib/play/question.svelte`, `lib/play/refusal.test.ts` |
| 18 | **Two over-wide permissions closed.** `captcha_enabled` defaulted to *true* on `/quiz/start`, where `check_captcha` then raised `AttributeError` out of `join_game` because `settings` was config.py's uncalled `lru_cache` wrapper — fixed, defaults off, refused without a provider key. The Excel export was open to any signed-in user while the view page hid the answers from a non-owner; **owner-only since 2 Oct** on François's call (D18). I had narrowed it on 1 Oct on a misreading of the markup and reverted it — this time it is the decision | `routers/quiz.py`, `socket_server/helpers.py`, `routers/eximport.py` |
| 19 | **Deleting an image gives the space back.** `storage_used` was only ever incremented — by the worker, once per upload — and nothing anywhere subtracted it, so it was a lifetime upload counter and the quota a lifetime cap. Enforcing the quota turned that into a real lockout. The delete endpoint releases the bytes, and taking an image off a question now deletes the orphan once nothing references it instead of merely unlinking it | `routers/storage.py`, `worker/storage.py`, [`docs/uploads.md`](docs/uploads.md) |
| 20 | **Deleting a quiz frees its images.** Both delete paths matched image keys with a regex that only described upstream's old double-key form, so for every modern upload it matched nothing: a deleted quiz, and every expired anonymous quiz, left its images in storage permanently and still charged to the owner. One reference-counted helper now serves all three paths | `frogquiz/helpers/__init__.py`, `routers/quiz.py`, `worker/storage.py` |

## Open — before sharing

- [ ] **Run `MVP.md` §4.1 on the deployed site.** Nobody has. It is the only part that can still reorder the rest
- [ ] **Real mail end to end**: register → confirm → reset, with `MAIL_*` set on the
      production API. Send to **francois.prevot@hotmail.com** (François, 2 Oct) —
      external and strict about SPF/DKIM, so a relay misconfiguration shows up.
      Steps in [`DEPLOY.md`](DEPLOY.md#testing-it-for-real); check spam on both mails
- [ ] **Confirm the `worker` container runs in production**, or the 30-day deletion the anonymous copy promises is not kept
- [x] **All decisions signed.** François signed D1 and D3–D15 on 2 Oct after asking for
      each to be explained; D2 and D16 are his "like Kahoot", D8, D9 and D18 are his, D17
      was already his. Nothing in §4.0 is waiting on anybody
- [ ] **#3 Part A** — two more boxes are now true: *Player disconnect / rejoin* (row 16) and
      *Image upload* (row 15). The rest of Part A is either a hidden feature (video,
      `/import`, `/remote`, `/quiztivity`, `/moderation`, `/results`) or needs the deployed
      site. Part B's keep/cut decisions are recorded in [`docs/mvp-scope.md`](docs/mvp-scope.md)

## Found in the feature sweep — all cleared

The five findings from [`docs/feature-inventory.md`](docs/feature-inventory.md) are fixed:
the silent refused answer, the missing socket `disconnect` handler, the unfiltered Excel
export (owner-only since 2 Oct, D18), `check_captcha`, and the route that lived inside a
string literal. Rows 16–18 above. That doc is still the map of the whole surface.

## Decided — 2 Oct

- [x] **Non-owner answer key: locked to the owner** (D18). The view page hid the correct
      answers from a non-owner while the Download button beside it handed over a
      spreadsheet containing them, so any signed-in teammate could read the answers to a
      quiz they were about to play. `GET /eximport/excel/{id}` is now scoped to
      `user_id` (404, not 403, so it leaks nothing about the id), and the button sits
      behind `{#if is_owner}`. Pinned by `test_excel_export_is_owner_only` and a new
      `practice.e2e.ts` case that asserts both halves: the button is absent for a
      non-owner **and** the endpoint refuses them.
      I narrowed this endpoint once before on a misreading of the markup and reverted it;
      this time it is the decision, not a guess.

- [x] **#16, #17 and #19 closed** on François's say-so (2 Oct), each with a comment
      recording the evidence rather than a bare close. #18 was already closed.
- [x] **D8 contact address**: the `francois.prevot@frog.co` placeholder stands. Revisit
      only if frogQuiz goes outside the team.
- [x] **D9 login architecture**: an account is what makes a quiz permanent; no SSO yet.
      `frogquiz/oauth/` stays config-gated and unwired.
- [x] **Mail test recipient**: `francois.prevot@hotmail.com`. Steps in `DEPLOY.md`.

## Open — two unexplained e2e failures, same symptom

**Do not assume one cause.** They share a shape — the player does not get, or cannot act
on, the question — and that is exactly the reasoning that produced a wrong attribution on
2 Oct. Recorded together so the pattern is visible, not so it is explained.

- [ ] **`game-reload.e2e.ts › a player can reload twice and still be in the game`** failed
      once, in the 127-test run on 2 Oct (124 passed). It waits for an answer button after
      two reloads and did not get one. It passed in the three full runs before that, and
      the spec is untouched this session. **Re-run straight after: 3/3 clean in isolation**
      (12/12 counting the rest of that file), so it is not reproducible on demand — the
      same profile as the `editor.e2e.ts` item below.

- [ ] **`editor.e2e.ts › build a quiz by hand, save it, and play it` failed once**, in the
      first of four full-suite runs on 2 Oct (118/119; the second was 119/119). `final_results`
      came back with no key for question `0`.
      I attributed it to the fire-and-forget `start_game` race and said the fix closed it.
      **That was wrong**: measured afterwards, the *unfixed* spec passed 10/10 in isolation.
      So: 1 occurrence in 2 full runs, cause unknown, and the opposite profile to the
      earlier flake (which failed 2 in 10 *in isolation*) — do not assume one cause.
      The spec now asserts which question keys came back, and prints the payload, so a
      recurrence is readable rather than an opaque `TypeError`. Leave this open until it
      either recurs with that message or goes twenty full runs without appearing.
      Related harness defect, worth fixing on its own: `next()` in `e2e/sockets.ts`
      resolves a falsy payload to `{}` instead of `null`, which is why `finalResults`'
      own `not.toBeNull()` guard could not catch an empty result.

## Open — quality

- [ ] `svelte-check` in CI. Measured in a single run, 2 Oct: **1054 errors, 229 in our own
      code and 825 under `node_modules`** (mostly `bits-ui`). Reproduce with
      `npx svelte-check --output machine > out.txt`, then count `^[0-9]* ERROR` lines in
      that one file, with and without `node_modules` — the first attempt at this used two
      separate `svelte-check` runs and reported 339/331, which made our share look like
      half the problem instead of a fifth. The original note here (~300 ours, ~820 in
      `bits-ui`) was right.
      Ours cluster hard, so this is less open-ended than 229 suggests: `play/question.svelte`
      (20), `editor/RangeSelectorEditorPart` (18), `editor/OrderEditorPart` (16),
      `account/login` (15), `editor/ABCDEditorPart` (12) — the top five are 81 of them, and
      three of those five are editor parts for question types the MVP does not offer
      (RANGE, ORDER, VOTING are not in the editor's allowlist), so they are gated code that
      could be excluded rather than fixed
- [ ] The input tier on hidden routes (`/quiztivity`, `/edit/files`, controllers, Pixabay) still draws form fields at three different radii. An `fq-field` utility would fold in the un-themed `bg-gray-500` / `focus:ring-blue-500` drift at the same time
- [ ] `lib/components/ui/button/button.svelte` has two off-ladder steps (8px and 10px) from upstream. Defensible, but they are the last two
- [ ] Tailwind scans the repo's Markdown, so the word "rounded" in `CLAUDE.md` emits three dead CSS rules. Harmless; noted so nobody re-chases it

## After V1

- [ ] Azure single sign-on (`frogquiz/oauth/` is config-gated and kept)
- [ ] Internal wiki: tools, alternatives, pros and cons
- [ ] MVP2 — avatars, rank position, word cloud (issue #4, `BACKLOG.md`)
- [ ] More languages (D10): i18next and every `$t(...)` are in place; it is a translated `locales/<lang>.json` plus a picker
- [ ] Submit frogQuiz to the internal Use Case Hub

## Notes

**Lobby music.** The track is `frontend/src/lib/assets/music/1-128.mp3`, a 17-second loop
that has been in the tree since the fork. Its REUSE header credits *Marlon W (Mawoka)*
under MPL-2.0, so we are reusing upstream's asset, not one of ours — decided on 1 Oct:
fine for now. It is a static file, not a call to upstream's servers, so the
"upstream independence" rule in `CLAUDE.md` is not in play. Worth revisiting only if
frogQuiz is ever shown outside the team, where somebody may want a track the project
actually owns. Kahoot's own music is copyrighted and is not an option.

## Decisions taken this session

| | Decision | Who |
| - | --- | --- |
| D17 | `--primary` stays zinc; `CLAUDE.md` corrected rather than the palette | François |
| — | Only the podium's colours were wrong; the answer tiles, ambient background and neutral scheme stay | François |
| — | Player feedback shows correct/wrong, points **and** place | François |
| — | The editor needs no drawer below `lg`: the column of cards is the navigation, as in Forms and Kahoot | François |
| — | True / False added as a preset over ABCD | François |
| — | `card.svelte`, `sidebar.svelte` and `question-strip.svelte` deleted rather than left dead | François |
| — | The ToS keeps its placeholder address for now (D8 stays open) | François |
| — | Reuse upstream's lobby track rather than sourcing or synthesising one | François |
| — | Kahoot's round sequence exactly: answers → scoreboard → next question | François |
