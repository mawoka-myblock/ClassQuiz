# FrogQuiz Backlog

Living backlog of feature ideas, gaps, and planned work, grounded in a comparison against Kahoot! and Mentimeter (the two products FrogQuiz sits between: game-show quizzing and live audience polling/presentation).

Format: each backlog section is a milestone. Items are one-liners with a short rationale; move an item to "Done" (or delete it) once shipped, and log the actual change in `CHANGELOG.md` as usual.

---

## Reference: Kahoot! — value proposition, journey, features

**Value proposition**: turn a room (physical or remote) into a live game. The host's screen is the shared spectacle (question, timer, music, podium); everyone else's device is just a game controller. Optimized for energy, competition, and memorable "aha" moments — a teaching/training tool that feels like a party game.

**Core user journey**:
1. Host picks or authors a "kahoot" (quiz) in an editor with question templates.
2. Host starts a live session, gets a 6-digit game PIN + shareable link/QR.
3. Players join on any device via a join page (`kahoot.it` + PIN), type a nickname — no account needed.
4. Host controls pacing question-by-question; the big screen shows the question, shape/colour-coded answers, and a countdown; players see only shapes/colours on their phone and tap.
5. Points are speed-weighted (faster + correct = more points); after each question the host screen shows an answer distribution and a live leaderboard.
6. Session ends with a podium (top 3) celebration and a full results/report export for the host.
7. Optional: assign the same quiz as **self-paced homework/challenge** (players go through it solo, at their own pace, over a longer window).

**Notable features**:
- Question types: multiple choice, true/false, multi-select, puzzle/reorder, type-answer (open text), slider/numeric-range guess, poll (no right answer), and content-only "slide" info screens.
- Speed-based scoring with streak bonuses; podium ceremony with confetti/music.
- Team mode (players cluster into teams sharing one device/score).
- Ghost mode (compete against a previous session's scores).
- Media-rich questions: images, video, audio per question.
- Question bank / question templates and a "generate with AI" quiz builder.
- Reports: per-player and per-question breakdowns, exportable (spreadsheet), used for grading/assessment.
- Kahoot library import/marketplace of public quizzes; discovery/search of others' public content.
- Works without an account for players; account required for hosts to save/host.
- Branded/sponsored kahoots, certificates, integrations (Teams/Zoom/Google Classroom) — enterprise-tier, less relevant here.

---

## Reference: Mentimeter — value proposition, journey, features

**Value proposition**: turn a room into a live *conversation*, not a competition. There's no winner — the point is instant, anonymous, aggregate feedback that becomes the visual centerpiece of a presentation (a poll result, a word cloud, a Q&A queue) rather than a game screen. Built for meetings, workshops, all-hands, and lecture-style audience engagement where honesty/anonymity matters more than speed.

**Core user journey**:
1. Presenter builds a "presentation" that interleaves normal content slides with interactive slides.
2. Presenter starts the session; a join code/QR is shown persistently in a corner of every slide (not a separate lobby step) — audience joins once and stays joined across the whole deck.
3. Presenter drives the deck like normal slides (arrow keys / clicker); each interactive slide accepts live input from the audience's phones with no per-question "start/stop" ceremony.
4. Responses render live and anonymously (bar chart growing in real time, word cloud reshaping as words are typed, a scatter/pin appearing on an image, a queue of submitted questions the presenter can upvote/mark answered).
5. No individual scoring, no leaderboard, no podium — the artifact of value is the aggregated result itself, which the presenter can screenshot/export/reuse.
6. Async use: a presentation can be shared as a standalone link for people to respond to on their own time (survey mode), not just live.

**Notable features**:
- Slide/question types: word cloud, open-ended text feed, multiple choice / bar or pie chart, ranking, scales (1–5 / NPS-style), Q&A with upvoting and "mark answered", 2x2 prioritization matrix, image/heatmap click-to-pin, quiz mode (Kahoot-like, exists but is the *secondary* mode), pin-on-image.
- Anonymity by default — no nicknames required, responses aren't tied to a visible identity in the room.
- "One join, many slides" — audience never re-scans a code per question.
- Templates for meeting formats (retro, icebreaker, all-hands Q&A, training).
- Live moderation of open-text/Q&A submissions (hide/approve before it hits the shared screen) to avoid inappropriate content going live.
- Export results (PDF/CSV/PPTX) after the session for a written record.
- Works embedded inside PowerPoint/Google Slides, not just standalone.
- Async/self-paced completion of a whole deck via link, no live host needed.

---

## What FrogQuiz already has (mapped against the above)

FrogQuiz inherits ClassQuiz's game-night core, which already covers most of Kahoot's spine:

| Capability | Status |
|---|---|
| PIN + QR join, no player account needed | ✅ (`frogquiz/routers/live.py`, live lobby) |
| Live host screen: question, timer, podium, confetti | ✅ (recently rebuilt, see CHANGELOG) |
| Per-question results: answer distribution + standings | ✅ (recently rebuilt as one card) |
| Question types | ✅ broad: `ABCD` (multi-choice), `CHECK` (multi-select), `RANGE` (numeric-slider guess), `VOTING` (poll, no right answer — Mentimeter-style), `TEXT` (open-text answer), `ORDER` (reorder/ranking), `SLIDE` (content-only, no answer) — see `frogquiz/db/models.py:138` |
| Self-paced / homework mode | ✅ `practice` route + `results.py` — solo play outside a live session |
| Import from Kahoot's own format | ✅ `frogquiz/kahoot_importer/` |
| Public gallery / discovery of others' quizzes | ✅ `explore` + `search` routes (kept per Feature triage in CLAUDE.md) |
| Anonymous quiz creation & hosting | ✅ shipped recently (no-account quiz authoring, claim-later flow) |
| Results export | ✅ host-side export controls on the podium screen |
| Physical/remote buzzer hardware | ✅ but slated to hide per Feature triage (`box_controller`, `remote`) — internal-tool, low priority |
| Editor for authoring questions with media | ✅ `editor.py` / `frontend/src/routes/edit` |
| Quiztivity (video-driven interactive quiz) | ✅ `frogquiz/quiztivity` — closer to a "watch + answer" hybrid, no direct Kahoot/Menti analogue |

What's **missing or thin** relative to both references:

- **No genuinely anonymous *live* response mode.** `VOTING` exists as a question *type* but the whole session is still framed as a scored, nicknamed game (PIN → lobby → podium). There's no "no names, no scoring, just show me the aggregate" *session mode* — Mentimeter's actual core mechanic.
- **No word cloud.** No question type aggregates free-text into a live-reshaping cloud; `TEXT` answers are scored right/wrong, not visualized as a corpus.
- **No live Q&A / upvoting queue.** No way for an audience to submit questions to a presenter and have the room upvote which get answered.
- **No "one join, many slides" flow.** Every FrogQuiz session is lobby → sequential questions with a fresh per-question state machine; there's no lightweight "join once, presenter free-flows through mixed content+interactive slides" pattern.
- **No rating/scale question type** (1–5, NPS-style) — distinct from `RANGE` (which is a numeric *guess-the-answer* game mechanic, not a subjective scale).
- **No 2x2 / prioritization-matrix or image-heatmap/pin-on-image question type.**
- **No live moderation queue** for open-text/Q&A before it hits the shared screen — relevant once free-text or Q&A ships, to avoid something inappropriate landing on the projector mid-meeting.
- **No speed-based/streak scoring nuance** — worth checking whether current scoring already rewards speed; if not, it's a small, high-visible-impact gap for the "game night" use case specifically.
- **No team mode** (shared-device team play) or **ghost mode** (replay against a past session).
- **No PPTX/Slides embedding** — not relevant for an internal tool.

---

## MVP1 working set

The work still open for MVP1, ahead of the MVP2 list below. Priorities are P0 (blocks a
path that is otherwise built), P1, P2.

### Status

| # | Item | Priority | State |
| - | ---- | -------- | ----- |
| — | Button wrappers forward `class`/`variant`/`size`/`label` | prep | **Done** |
| — | Install shadcn `dialog` + `collapsible` | prep | **Done** |
| 1 | Anonymous host hits a login wall | P0 | **Done**, verified locally |
| 2 | Editor "+" add-question button | P2 | **Done**, visual pass outstanding |
| 3 | Merge Explore and Search | P1 | **Done**, visual pass outstanding |
| 4 | Play/host UX, anonymous and logged-in | P1 | **Done** — [#16](https://github.com/ogfrench/frogQuiz/issues/16); live-game check owed |
| 5 | Design the view page `/view/[quiz_id]` | P2 | **Done** — [#17](https://github.com/ogfrench/frogQuiz/issues/17); browser-checked 2026-09-29 (`MVP.md` §4.4) |
| 6 | Merge `/my-quizzes` into `/dashboard` | P2 | **Done** 2026-09-29, in the other direction: `/dashboard` redirects to `/my-quizzes` (MVP.md D1) — [#18](https://github.com/ogfrench/frogQuiz/issues/18) |
| 7 | Play modal front-end fix | P2 | **Done** — was the same component as 4, landed with it |
| 8 | Visual pass at 390/834/1440 | P1 | Open — [#19](https://github.com/ogfrench/frogQuiz/issues/19); overflow half now automated (`responsive` e2e spec, all pages pass) |
| 9 | Fix the live-game bugs the e2e suite found | P0 | **Done** 2026-09-18, all 63 e2e green; see [`docs/e2e-findings.md`](docs/e2e-findings.md) |
| 10 | Fix the ownership/editor bugs the e2e suite found | P1 | **Done** 2026-09-18, same doc |

Tracked on GitHub under the MVP1 umbrella, [#3](https://github.com/ogfrench/frogQuiz/issues/3).

Items 2 and 3 are code-complete and green (tests, eslint, production build) but have
**not** been driven in a browser at 390/834/1440. That check is batched and still owed;
until it happens neither is promoted to Done in `docs/redesign-status.md`.

Verification constraints worth knowing before picking anything up:

- **There is now a full local stack.** `bash e2e/run.sh` brings up Postgres, Redis
  (fakeredis), Meilisearch, the API and the frontend on Windows with no Docker or WSL, and
  runs the Playwright suite against it; `KEEP_UP=1` leaves it running for manual checks.
  Items 2–4 can now be driven in a browser locally, live games included. (Before
  2026-09-18 there was no local backend, which is why those items say "visual pass
  outstanding".)
- **The Vite proxy cannot reach the deployed backend from this environment**: TLS
  interception makes it fail with `self-signed certificate in certificate chain`. The local
  stack above is the way around it.

### ~~P0 — Live-game bugs found by the e2e suite~~ (done)

All fixed on 2026-09-18, along with every Low item. How each one was fixed, and the two
found and deliberately left open (the un-awaited captcha check, and the editor's
question-cap message), are in [`docs/e2e-findings.md`](docs/e2e-findings.md). The plan
as it stood is kept below. In the order they were done:

1. **H1 — Concurrent answers overwrite each other.** Make `set_answer` atomic (an `RPUSH`
   per answer, or a Lua/`WATCH` transaction). This also fixes the knock-on effects on
   "everyone answered", the double-answer check and the projector podium.
2. **H2 — A reloaded player can never score again.** Save the session before emitting
   `time_sync` in `rejoin_game`, and default `ping` to 0 in `submit_answer`.
3. **H4 / H5 — Players can take host control.** Gate `register_as_remote` (or remove it
   with the box-controller feature it serves), and delete or authenticate
   `GET /quiz/join/{pin}`.
4. **H3 — The projector podium tallies scores client-side.** Read the server's
   `player_scores` instead.
5. **M1 / M2 / M5 / M6 — Server-side validation.** Bound the timer, require answers,
   reject empty quizzes, and enforce the timer and `question_show` in `submit_answer`.
6. **M3 / M4 / M11 / M12** — kick, room-less broadcasts, the rejoin cookie, and the
   nickname race.

### ~~P1 — Ownership and editor bugs found by the e2e suite~~ (done)

H6 (anonymous quizzes can't be edited; blank page), M7 (Save allows a question with no
correct answer), M8 (signing in hides your unclaimed quiz), M9 (sign-up drops
`returnTo`), M10 (the editor's Back link leads to a login wall). Details in
[`docs/e2e-findings.md`](docs/e2e-findings.md).

### ~~P0 — An anonymous host hits a login wall when starting a game~~ (done)

**Done.** The guard is gone and the Save-results button is hidden for an anonymous host,
which is the decision the last paragraph below left open. Verified locally:
`/admin?token=…&pin=…` returns 200 with `signed_in:false` server-rendered, where it used
to 302 to `/account/login`. The rest of the host path still needs a deployed check — see
the P1 play/host item. Kept below for the reasoning.

Creating a quiz at `/create?anon=true` works, but pressing play redirects to
`/account/login`, so the account-free path dead-ends at the one screen it exists for.

Confirmed: it is the route guard and nothing else.
`frontend/src/routes/admin/+page.server.ts` redirects on `!email` with no escape hatch,
where `frontend/src/routes/create/+page.server.ts` checks `!email && !anon`. Everything
underneath already works without a session:

- `POST /api/v1/quiz/start/{id}` accepts `X-Anon-Secret` in place of a login, and
  `lib/dashboard/start_game.svelte` **already sends it** when it holds one.
- The socket server's `register_as_admin` checks no user at all — admin rights come from
  holding the right `game_pin` + `game_id`.

The host screen has to keep working with no session for its whole lifetime, not just at
the moment it loads. One thing to decide while doing it: **the "save results" button at
the end.** `save_quiz` is a bare socket emit and `GameResults.user` is nullable, so an
anonymous host's save will succeed — and write a row nobody can ever read, because
`/api/v1/results/*` is user-scoped. Either hide the control for an anonymous host, or
give the save somewhere to go. Silently writing an unreachable row is the wrong third
option.

Do this before the dashboard merge (P2 below), or the merged logged-out dashboard ships
a play button that dead-ends.

### ~~P1 — Merge Explore and Search into one page~~ (done)

**Done.** Verified against a local stub carrying the deployed backend's real payload:
browse renders the listing, `?q=te` sends no request, `?q=test` renders highlights as
`<mark>`, an unmatched query renders the empty state, and `/search?q=test` 302s to
`/explore?q=test`. A hostile title renders escaped. Two bugs fixed in passing — the
stringified `imported_from_kahoot` in `_formatted`, and Explore parsing a failed
response as if it had succeeded. **Still outstanding**: the 390/834/1440 visual pass.

`/explore` survives; `/search` redirects to it. One page: a search box at the top, and
the recent listing (empty query, `created_at:desc`) when nothing has been typed.

Explore is the survivor, so `explore_page.*` stays and `search_page.*` folds into it.
This dissolves rather than fixes the coupling noted in `CLAUDE.md` — that
`lib/search-card.svelte` renders `explore_page.*` strings while showing Search results
stops mattering once only one page is left.

### ~~P1 — Play/host UX, anonymous and logged-in~~ (done)

**Done**, with the modal rebuild and the parity audit both landed under #16. Four bugs
fixed beyond the redesign: the custom field was not URL-encoded, any failed start logged
a signed-in host out, the lobby's fullscreen QR overlay was `w-screen h-screen`, and the
host shell was `min-h-screen`. `slide.svelte` and `voting_results.svelte` are now inside
`fq-stage` — they were the last two host surfaces outside it. The parity table is in
`docs/redesign-status.md`.

**Still owed**: hosting a real game through it, which needs the deployed stack, plus the
390/834/1440 pass ([#19](https://github.com/ogfrench/frogQuiz/issues/19)).


The logged-in dashboard is the reference; the anonymous side should match it.

**`lib/dashboard/start_game.svelte` is a full rebuild, not a `Dialog` wrap.** It is the
shared hosting entry point for both audiences and what the dashboard merge (item 6)
mounts for anonymous users, and it is entirely pre-redesign. Verified in the file:

- L95 is `fixed … w-screen h-screen bg-black/60 z-50 text-black` — `w-screen` and
  `h-screen` are both on `CLAUDE.md`'s "things that keep coming back" list, and
  `text-black` is the third.
- `bg-white` at L146 and L158, `bg-green-500` at L208, `bg-blue-600`/`bg-gray-200`
  toggles at L117-124 and L190-197.
- Two untranslated strings, and `alert('Starting game failed')` at L66 as the whole of
  the failure path.

Rebuild it as a `Dialog` on tokens, `Label`/`Input`/`Button`, translated strings and an
inline error. **Preserve the anonymous-secret logic at L38-39 and L67-69 verbatim** — it
already works and is what makes anonymous hosting possible at all.

Then audit the rest of the host path for parity. The differences that are deliberate for
an anonymous host, and should stay: no lobby resume card, no Save results (see the P0
item), no analytics. Everything else should be identical. Record the resulting list in
`docs/redesign-status.md`.

`slide.svelte:38` and `voting_results.svelte:55` are the two host surfaces still outside
`fq-stage`. Check whether voting and slides are behind a disabled flag before spending
time there — `docs/mvp-scope.md` has the answer.

### P2 — Merge `/my-quizzes` into `/dashboard` as its logged-out state

> **Done 2026-09-29, the other way round:** `/my-quizzes` is the surviving URL and
> `/dashboard` redirects to it (decision D1 in `MVP.md`). The notes below are the
> original plan, kept for the reasoning.

Built from the per-device `localStorage` list, local only, with no account prompt
required. Drops the `/dashboard` login guard and removes `/my-quizzes` as a separate
route.

- **Carries over**: quiz list, create, host/play, delete, client-side filter.
- **Excluded for anonymous**, because each needs an account server-side: Kahoot import
  (`/import` is auth-gated), results history and analytics (`/api/v1/results/*`), media
  library (`/dashboard/files`).
- **Anonymous-only additions**: per-quiz expiry, claim-to-keep.

### P2 — Play modal front-end fix (same work as the play/host UX item above)

Specified 2026-09-16: it's the host's start-game popup
(`lib/dashboard/start_game.svelte`), not the player's join screen. It predates the
shadcn redesign — hand-rolled checkbox toggles, a raw `<div>` overlay instead of
`Dialog`, hardcoded `text-black`/`bg-white`/`bg-green-500`, `marck-script` on the CTA,
and `w-screen`/`h-screen` (both on the CLAUDE.md "things that keep coming back" list).

Rebuild on shadcn `Dialog`/`Button`/`Card`/`Input`/`Label` plus a new `Switch`
component, matching the editor/dashboard visual language. Also folds in a scope cut:
drop the Normal/Old-School mode picker (game mode hardcoded to `kahoot`; the API still
accepts `normal` if it's ever wanted back) and drop the captcha toggle, which is dead
UI while hCaptcha is off at the config level. Keeps the custom field, randomize-answers
toggle, and start/spinner behaviour.

Tracked as [ogfrench/frogQuiz#16](https://github.com/ogfrench/frogQuiz/issues/16).

**This and the P1 play/host UX item above are the same component**, so they are being
done as one piece of work under #16. Two things #16 predates and that the rebuild has to
respect: the modal is now on the anonymous path, since the P0 guard is gone — so the
anon-secret logic at L38-39 and L67-69 must survive verbatim — and the host-path parity
audit rides along with it.

### P2 — Design the view page (`/view/[quiz_id]`)

Currently unredesigned. `docs/redesign-status.md` used to record it as "reviewed and
needed no change"; that claim was wrong and has been corrected. It now also carries the
anonymous-owner panel (expiry, claim, delete), so design that in rather than around it.

What is actually there, verified in the file:

- **Shell**: use `fq-section`, not `fq-stage`. `fq-stage` is `min-height:100dvh` plus
  `justify-center` — a projector utility, wrong for a 443-line document. Reading column
  `max-w-2xl mx-auto`, header as a `Card`.
- **Questions**: replace `lib/collapsible.svelte` with the shadcn `Collapsible` (now
  installed). Audit its consumers first — if `/view` is the only one, delete it. Budget
  styling time: `Collapsible` is headless and gives none of the current bordered-row
  look. Drop the dead `<style>` block and its `var(--gray-light, #eee)` reference to a
  variable that does not exist.
- **Anonymous owner panel**: it is currently nested *inside* the Download button's
  wrapper div; lift it into its own `Card`. Claim-failure `alert()` at L104 → inline
  translated error. Sign-up CTA at L314-319 (a raw `<a>` hand-styled as a button) →
  `Button href=`. Delete → `variant="destructive"`, reachable now that the button
  wrappers forward `variant`.
- **Accessibility**: the icon-only Play buttons at L183-210 and L215-237 need `label`,
  which the `gray` wrapper now forwards.
- **Colours**: L343 `bg-white dark:bg-gray-700` → `Card`/tokens; L384-387
  `shadow-blue-500`/`shadow-yellow-500` → a token ring; L405/L415 `bg-gray-300
  dark:bg-gray-500` → `muted`. **Keep** the `ANSWER_COLORS` inline styles at L380-383 —
  that is answer identity, not theming.
- Remove the stray `console.log(auto_expand, 'autoexpand')` at L40.

### ~~P2 — Editor: a "+" add-question button below the questions~~ (done)

Google Forms style. Purely UX, and additive — the left rail keeps its add control.
Assumed to open the same type picker, so there is one behaviour rather than two.

**Done.** Both controls open the same picker, which is now the shadcn `Dialog`. The
rail's own button was also fixed: it sat inside the scrolling list, so it scrolled out of
reach on a long quiz, and is now a pinned footer. Compiles and lints clean; **the visual
check at 390/834/1440 is still outstanding** — the editor needs a backend to render.

### Note on feature consolidation

Gonçalo has stated he is comfortable consolidating features that exist on master where
needed, including the Explore/Search merge above. Recorded here as his position.
`CLAUDE.md` makes this a joint call with François, so **the blanket form needs François's
agreement before it supersedes that rule.** The Explore/Search merge above is the
specific case he has signed off on, not a general licence.

---

## MVP2 Backlog

Scoped for FrogQuiz as an **internal team tool** — prioritizing the gaps that unlock genuine meeting/workshop use (Menti-style) alongside the game-night use case already covered, over enterprise features (branding, integrations, certificates) that don't apply here.

### High value, low-to-medium effort
- [ ] **Word cloud question type.** New `QuizQuestionType.WORDCLOUD` (or extend `TEXT`) whose live host/results view renders submitted words as a reshaping cloud instead of a scored answer list. This is Menti's single most requested and most legible feature, and FrogQuiz already has the text-submission plumbing (`TextQuizAnswer`) to build on.
- [ ] **Rating/scale question type.** A 1–5 or 1–10 subjective scale (distinct from `RANGE`'s "guess the right number" game mechanic) with a simple average/distribution result view — useful for team retros and feedback sessions, not just quizzes.
- [ ] **"Anonymous session" mode toggle.** A per-session flag that suppresses nicknames on the host screen and skips scoring/podium entirely, reusing the existing `VOTING`/poll machinery but changing the *session framing* — turns FrogQuiz into a genuine Menti-style feedback tool for meetings, not just a quiz with an ungraded question type.
- [ ] **Quiz-style picker at create/host time: "game" vs "presentation" mode (naming TBD).** Let the host choose a Kahoot-style scored game vs a Menti-style unscored presentation/feedback session, with clearer labels than the old "Normal/Old-School" picker that was dropped from `start_game.svelte` during the P2 play-modal rebuild (game mode is currently hardcoded to `kahoot`, though the API still accepts `normal`). Overlaps with the anonymous-session-mode item above — worth designing as one choice (style + framing together) rather than two separate toggles.

### Medium value, medium effort
- [ ] **Live Q&A / upvote queue.** A session mode where attendees submit questions instead of answers, others upvote, and the host sees a ranked list to work through live — the single biggest missing all-hands/workshop use case Menti covers and Kahoot doesn't.
- [ ] **Lightweight moderation for open-text submissions.** Once word cloud / Q&A / open `TEXT` responses can appear live on a shared screen, add a host-side approve/hide step before a submission renders — small effort, closes an obvious "something inappropriate hits the projector" risk for an internal tool used across a whole team.
- [ ] **"One join, many slides" session shape.** Explore whether live sessions can support a mixed deck (content slides + interactive slides) under a single join/PIN, rather than the current lobby-then-sequential-questions state machine — this is what makes Menti feel like "presenting," not "gaming." Larger architectural item; worth a design spike before committing.

### Lower priority / nice-to-have
- [ ] **Team mode** (shared-device team scoring) for the game-night use case.
- [ ] **Ghost mode** (asynchronously compete against a previous session's recorded pace/scores).
- [ ] **Image pin/heatmap question type** ("click where on this image...") — Menti feature, no current equivalent.
- [ ] **2x2 prioritization matrix question type** — niche but common in team retros/planning.
- [ ] Audit current scoring for speed-bonus/streak behavior and document/tune it if missing — cheap to verify, meaningful to the game-night feel if absent.

### Explicitly out of scope for MVP2 (enterprise/public-product features, not needed for an internal tool)
- AI-generated quiz authoring, question marketplaces/branded content, PPTX/Google Slides embedding, Teams/Zoom/Classroom integrations, certificates, sponsored content.
