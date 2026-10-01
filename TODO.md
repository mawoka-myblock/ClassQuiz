<!--
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

# TODO — live tracker

Where the work actually stands. [`MVP.md`](MVP.md) is the plan and holds the decisions;
this file is the running state, updated as things land.
Audit that produced most of it: [`docs/audit-2026-10-01.md`](docs/audit-2026-10-01.md).

**Branch:** `ccr-370df3e4-c44t1l` · **Suites:** 121 unit · 113 e2e · 142 backend (1 skipped)

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
| 15 | **Uploads have limits, and there is still no file manager.** There was no server-side size cap at all (`size = 0` went into storage, the only limit was Uppy's in the browser, and the endpoint takes anonymous uploads) — and the browser's cap was not applied either, because `restrictions` is an Uppy *Core* option and was passed to the Dashboard plugin. 8MB per image, enforced at Caddy, on `Content-Length`, and on the counted bytes; the quota counts the file in hand; `/raw` aborts mid-stream; `video/mp4` behind a flag | `frogquiz/config.py`, `routers/storage.py`, `frogquiz/__init__.py`, `Caddyfile*`, `lib/editor/uploader.svelte`, [`docs/uploads.md`](docs/uploads.md) |

## Open — before sharing

- [ ] **Run `MVP.md` §4.1 on the deployed site.** Nobody has. It is the only part that can still reorder the rest
- [ ] **Real mail end to end**: register → confirm → reset, with `MAIL_*` set on the production API
- [ ] **Confirm the `worker` container runs in production**, or the 30-day deletion the anonymous copy promises is not kept
- [ ] **François signs D1–D15**, or says which to put back. Everything hidden is reversible in one edit
- [ ] **D16**: do players need the question text on their own phone? Right in a room, wrong on a call
- [ ] **Close #16** — the start-game modal was rebuilt and driven in a browser

## Open — found in the feature sweep, not yet fixed

See [`docs/feature-inventory.md`](docs/feature-inventory.md) for the whole surface.

- [ ] **A refused answer is silent.** The server emits `already_replied` and `question_not_active`; nothing in the frontend listens, so a player who answers twice or answers after the reveal still sees "Answer locked in"
- [ ] **No socket `disconnect` handler.** A closed tab stays in the player set, so "everyone has answered" never fires again once somebody leaves without pressing Leave — the host waits out every timer for the rest of the game
- [ ] **`/eximport/excel/{quiz_id}` has no owner filter**: any signed-in user can download any quiz by id, answers included. Consistent with "unlisted, not private", worth a decision rather than a silence
- [ ] `check_captcha` returns `True` when no captcha secret is set. Inert while `captcha_enabled` is hard-coded off
- [ ] `routers/results.py:62-84` — a route whose whole function body is inside a string literal

## Open — quality

- [ ] `svelte-check` in CI, once the ~300 errors in our own code are down (another ~820 are inside `bits-ui`)
- [ ] The input tier on hidden routes (`/quiztivity`, `/edit/files`, controllers, Pixabay) still draws form fields at three different radii. An `fq-field` utility would fold in the un-themed `bg-gray-500` / `focus:ring-blue-500` drift at the same time
- [ ] `lib/components/ui/button/button.svelte` has two off-ladder steps (8px and 10px) from upstream. Defensible, but they are the last two
- [ ] **No UI for deleting an uploaded image.** `DELETE /api/v1/storage/meta/{file_id}` exists and is owner-filtered, and replacing a question's image orphans the old row, but nothing in the app lets someone reclaim their own 256 MiB. The quota is now enforced per upload, so this is what a person hits when it fills. The media library that would have shown it is deliberately hidden (see [`docs/uploads.md`](docs/uploads.md)) — this wants a smaller answer, not that page back
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
