<!--
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

# Redesign status, surface by surface

What has been redesigned, what has not, and why. Scope decisions are in
[`mvp-scope.md`](mvp-scope.md); this page is only about visual and interaction
work. 44 routes exist.

The bar for "done" here is deliberately high, because the cheap version of this
table is worthless: **redesigned, then driven in a real browser at 390, 834 and
1440, in a real three-player game where that applies, with no horizontal
overflow at any width.** Anything less is in one of the other tables.

---

## Done

| Surface                | Route            | What changed                                                                                                                       |
| ---------------------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Host lobby             | `/admin`         | One centred composition: giant join code, QR beside it, animated player chips, kick as a labelled button                           |
| Host question          | `/admin`         | Rebuilt; was the only game surface missing `fq-stage`, so it sat flush against the top of the projector with the bottom half empty |
| Per-question results   | `/admin`         | Horizontal bars replacing vertical ones whose 45°-rotated labels collided; correct row marked with a tick and a ring               |
| Podium                 | `/admin`         | Three-place podium building 3rd→2nd→1st, winner highlighted, confetti timed to their arrival; viewport-scaled blocks               |
| Player join and answer | `/play`          | Answer tiles with shape, colour and pressable body; "you're in" confirmation; locked-in and time's-up states                       |
| Editor                 | `/edit`          | Canvas shows the real game tiles; question navigation in the shell at every width; measure-capped canvas                           |
| My Quizzes             | `/my-quizzes`    | The old dashboard list, merged with the signed-out browser list 2026-09-29 (D1): one page for both states, "On this browser" with Claim when signed in, the 30-day notice and account CTA when signed out, Delete in a dialog. `/dashboard` redirects here. Verified 2026-09-29 at 390/834/1440 in both themes, signed in and out |
| Login                  | `/account/login` | Both steps on shadcn Label/Input/Button                                                                                            |
| Quiz view page         | `/view/[quiz_id]` | Header card with Start as the one primary action, owner-only Edit/Delete and answer key, expandable anonymous-quiz banner, questions drawn as read-only editor canvases. Verified 2026-09-29 at 390/834/1440 in both themes as anonymous owner, account owner and visitor. The Download dialog it opens is still pre-redesign |

| Landing | `/` | Verified clean at both widths and themes |
| Register | `/account/register` | Rebuilt on the same Card/Label/Input/Button primitives as login |
| Results history | `/results`, `/results/[result_id]` | Table rebuilt on theme tokens in an `fq-scroll-x` container; real empty state with a way out of it |
| Create | `/create` | Verified clean |
| Kahoot import | `/import` | Rebuilt as two stacking cards; styled file picker; no invalid ring on an untouched field |
| Media library | `/dashboard/files` | Verified clean |
| Password reset | `/account/password-reset`, `/account/reset-password` | Swept with import |
| Account settings | `/account/settings` | Rebuilt from `grid-cols-6` to a single column of section cards; sessions table in a scroll container; initial-letter avatar fallback |

Two cross-cutting systems came out of this and now apply to every surface above:

- **Answer palette** — four pastel hues in `src/lib/play/answer_colors.ts`, derived
  in OKLCH. Was the same hex array copy-pasted into six files. This page previously
  said the palette was "validated for colour-vision separation". It is not, and an
  earlier commit in this branch corrected the same claim in the source: under
  deuteranopia coral and green differ by 4 of 255. Four hues at one lightness cannot
  be separated by a dichromat. Accessibility here rests on the shape channel, which
  `answer_colors.test.ts` now pins deliberately.
- **Projector type** — `fq-display`, `fq-answer`, `fq-meta`, `fq-pin` in `app.css`,
  clamped vw. Replaced breakpoint ladders that stopped growing at 768px, roughly
  where a projector starts.
- **Spacing** — `fq-stage` / `fq-section` and `--fq-space-*`.

---

## In scope, not done

- **Explore** (`/explore`) — rebuilt on shadcn `Card` and theme tokens when Explore and
  Search were merged into it, and its four render modes (browse, too-short, results with
  highlights, empty) were verified server-side against a stub carrying the deployed
  backend's real payload. It is here rather than in Done because it has **not** been
  driven in a browser at 390/834/1440, which is what this page means by verified.
  `/search` is now a 302 into it and renders nothing of its own.
- **Editor add-question control** — the rail's button moved out of the scroll container
  and a second one added at the end of the canvas; the type picker is the shadcn
  `Dialog` now. Same gap: compiles and lints, not yet driven at the three widths.
- **Host start-game modal** (`lib/dashboard/start_game.svelte`, opened from `/dashboard`)
  — rebuilt on shadcn `Dialog`/`Button`/`Card`/`Input`/`Label`/`Switch`; the Old-School
  mode picker and the (already-inert) captcha toggle were dropped in the same pass, see
  [ogfrench/frogQuiz#16](https://github.com/ogfrench/frogQuiz/issues/16). Not yet driven
  at the three widths.

`/edit/files` was reviewed and needed no change. `/view/[quiz_id]` was once listed here
as reviewed and needing no change; that was wrong. It has since been redesigned and
verified (see Done).

## Skipped, because the feature is cut

All of these 404 behind a flag or a route guard. See [`mvp-scope.md`](mvp-scope.md)
for how to turn any of them back on.

| Surface               | Route                                                                                                   |
| --------------------- | ------------------------------------------------------------------------------------------------------- |
| QuizTivity            | `/quiztivity/create`, `/quiztivity/edit`, `/quiztivity/play`                                            |
| Box controller        | `/controller`, `/account/controllers/*` (4 routes)                                                      |
| TOTP and backup codes | `/account/settings/security`                                                                            |
| Moderation            | `/moderation` — 404s in its loader; its API is separately gated on the `mods` allowlist, which is empty |

`/remote` and `/practice` are alternate play modes nobody on the team uses. They
are not flag-gated and are not redesigned. Deciding what to do with them is open.

---

## Skipped, deliberately, while still live

| Surface          | Route                        | Why                                                                                                                                                                                                                                                                                                                                                       |
| ---------------- | ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Docs             | `/docs` and 7 pages under it | Layout untouched, but the copy was not left alone: all eight carried upstream's "the open-source quiz-application" description and two described a different page entirely, two told you to `git clone mawoka-myblock/ClassQuiz`, and the attribution page credited nine named people for work on frogQuiz they never did. See the identity section below |
| Public user page | `/user/[user_id]`            | Nobody links to it internally                                                                                                                                                                                                                                                                                                                             |
| OAuth error      | `/account/oauth-error`       | Layout untouched — OAuth renders nothing today, by config. Its "open an issue" link pointed at upstream's tracker and now points at ours                                                                                                                                                                                                                  |
| Video editor     | `/edit/videos`               | Reachable only from the uploader's video path                                                                                                                                                                                                                                                                                                             |

---

## Hosting with and without an account

Both are supported end to end. The differences below are deliberate, and each was
checked against the endpoint rather than assumed — so if one of them ever looks like a
bug, this is the reason it is not.

| Capability | Signed in | Anonymous | Why |
| --- | --- | --- | --- |
| Start a game | yes | yes | `start_quiz` takes an optional user and accepts `X-Anon-Secret` in its place |
| Run the game over the socket | yes | yes | `register_as_admin` checks no user at all — admin rights come from holding the right `game_pin` + `game_id` |
| Join QR code | yes | yes | `GET /utils/qr/{pin}` has no auth dependency |
| Spreadsheet export of answers | yes | yes | `export_quiz_answers(export_token, game_pin)` has no auth dependency |
| **Save results** | yes | **no, hidden** | Every route in `routers/results.py` requires `get_current_user`, and `GameResults.user` is nullable — so an anonymous save succeeds and writes a row nobody can ever read |
| **Analytics** | yes | **no** | Same: reads go through the user-scoped results routes |

Two notes on the Save-results case. The socket handler itself only checks
`session["admin"]`, so the backend still accepts the emit — hiding the button is a
frontend decision about not writing unreachable rows, not an authorisation boundary.
And an anonymous host still gets the podium and the export, which is most of what the
save was for.

**A difference that turned out not to exist.** Planning assumed anonymous hosts would
lack a "resume lobby" card that signed-in hosts had. There is no such card for anyone —
`grep` for it across `routes/dashboard/` and `lib/dashboard/` returns nothing. Recorded
so the assumption does not come back.

---

## Identity and metadata

Not visual design, but the same class of problem: what the app says it is. All of
this was inherited from upstream and had been through a global ClassQuiz→frogQuiz
find-replace, which in two places turned other people's work into claims about this
project.

| Thing                                               | Was                                                                                                                                     | Now                                                                                                                                                                                                                              |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Open Graph card                                     | Upstream's image: says "ClassQuiz", carries "By Mawoka" and his avatar                                                                  | Regenerated from the app's own mark. `og:image` was also _root-relative_, which crawlers will not resolve, so the card rendered imageless even after the image was right — both image tags are built from the request origin now |
| Favicon set                                         | "CQ" in upstream's chevrons                                                                                                             | Regenerated. `favicon.ico` was a PNG under an `.ico` extension; it is a real ICO wrapping the PNG                                                                                                                                |
| `twitter:image`                                     | Pointed at `opengraph-home.webp`, which was a PNG                                                                                       | Deleted the mislabelled file; both tags use the 1200×630 JPEG                                                                                                                                                                    |
| Font                                                | Never loaded — seven `@font-face` rules, seven 404s                                                                                     | All seven Inter subsets emit; `document.fonts.check` passes                                                                                                                                                                      |
| Tagline                                             | Two different ones at once: "Live quizzes for the room you are standing in" and "an internal quiz tool for running interactive quizzes" | One line in `app.html`, the manifest and `en.json`: "The free Kahoot alternative. Host interactive quizzes right from your browser."                                                                                             |
| `testimonials.svelte`                               | A real person, a real tweet URL, and quote text edited so an endorsement of ClassQuiz read as one of frogQuiz                           | Deleted. Nothing imported it, but it was one line from rendering                                                                                                                                                                 |
| `/docs/attribution`                                 | Upstream's contributor list with the same find-replace, so nine named people were credited for contributing to and translating frogQuiz | Rewritten to say the truth: frogQuiz is a fork, these people built the thing it is a fork of, their translations live upstream                                                                                                   |
| Clone URLs in `/docs/self-host` and `/docs/develop` | `git clone mawoka-myblock/ClassQuiz`                                                                                                    | `ogfrench/frogQuiz`                                                                                                                                                                                                              |

One upstream URL is deliberately kept: the box controller fetching its firmware
releases from `mawoka-myblock/ClassQuizController`. That is upstream's hardware and
upstream's firmware, so the link is correct; the feature is flag-gated off anyway.

---

## Languages

The app ships English only. See [`mvp-scope.md`](mvp-scope.md#languages) — this is a
scope decision, not a visual one, and it is **open** pending Gonçalo.

---

## What "verified" does and does not mean here

Worth being exact, because the phrase gets stretched:

- **Verified:** driven in Chromium via Playwright, real backend, real Postgres,
  real socket.io, three player contexts joining by PIN. Screenshots at 390, 834
  and 1440. `document.documentElement.scrollWidth > clientWidth` checked at each.
- **Not verified:** anything on the deployed site. The sandbox this work was done
  in cannot reach `frogquiz.xyz` — the egress policy blocks it — so nothing here
  describes production. Somebody has to open the real site.
- **Verified:** eight routes x two themes x two widths report no horizontal overflow,
  no touch target below the minimum (44px on coarse pointers, 24px otherwise) and no
  text below WCAG AA. Chasing the last of those to its cause was worth it: the
  remaining overflow was never layout, it was paint -- filters expanding an element's
  painted region past its box, and a wide table contributing paint through a scroll
  container that was itself working correctly.
- **Verified in dark mode:** the editor, at 390 and 1440. Doing this found a real
  bug rather than confirming a guess: `ckeditor5.css` sets its own text colour as a
  near-black constant, so the question title in the editor rendered black on a dark
  ground and was all but invisible. It is mapped onto the theme tokens now.
- **Not verified in dark mode:** the projector surfaces and the player screens since
  the type-scale change. They were checked in both themes when first built.
- **Covered by tests now.** This line used to read "there are no frontend tests,
  and the frontend CI job runs eslint only". There are 57 under vitest and the CI
  job runs them, alongside eslint. They cover the answer palette, question
  completeness, the theme tokens, reordering and the multiple-answer wire format —
  the things with real invariants, not the things that are easy to assert.
- **Not verified: anything rendered before the font was fixed.** Inter never loaded
  in any build until late in this branch — Tailwind v4 inlines an `@import`'s text
  but leaves its relative `url(files/...)` alone, so Vite emitted no `.woff2` at all
  and every `@font-face` 404'd. Every screenshot taken for this table before that
  fix was rendered in whatever `sans-serif` aliases to, which differs per OS. The
  surfaces were re-checked at 390 and 1440 afterwards and the layouts held, but that
  is a re-check, not the original verification.
