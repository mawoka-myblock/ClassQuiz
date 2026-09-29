<!--
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

# frogQuiz MVP — working checklist

For Gonçalo and François. Tick boxes as things land, and put your initials on the
decision lines. Audited against `master` at `9cd23820` on 2026-09-28.

**How this relates to the other docs.** [`docs/mvp-scope.md`](docs/mvp-scope.md) records
what has already been cut and why. [`docs/redesign-status.md`](docs/redesign-status.md)
records which screens are redesigned. [`BACKLOG.md`](BACKLOG.md) holds MVP2 ideas. This
file is the plan for getting from here to something we can share, and it supersedes the
"MVP1 working set" section of `BACKLOG.md` where the two disagree.

**Rules this checklist follows.**

- **Hide, don't delete.** "Hide" means take it out of navigation and, where it matters,
  404 the route through `DISABLED_ROUTES` in `frontend/src/hooks.server.ts`. The code
  stays in the tree.
- **"Remove" is a proposal, never an instruction.** Removing a feature that exists on
  master needs both of us (see `CLAUDE.md`). Every Remove below has two sign-off boxes.
- **Hiding a page does not close its API.** Where the endpoint matters, it says so.

---

## 1. The MVP in one line

> **Create → Edit → Start → Play → Finish → Return**, reachable from three surfaces —
> **Discover | My Quizzes | Join** — that look the same whether you are signed in or not.
> Signing in adds **My Account** and makes quizzes permanent.

| Surface | Signed out | Signed in |
| --- | --- | --- |
| **Discover** (`/explore`) | Browse and search public quizzes | Same |
| **My Quizzes** | Quizzes this browser created: create, edit, start, delete, see expiry | Quizzes on the account: same actions, plus claim anything this browser made |
| **Join** (`/play`) | PIN → nickname → play | Same |
| **My Account** | — (Sign in / Register instead) | Profile, password, sessions, delete account, sign out |

### What "anonymous" actually means today — the copy must say this accurately

An anonymous quiz is **stored on the server**, not in the browser. What the browser keeps
is the **ownership secret** (`localStorage`, see `frontend/src/lib/anon_quiz.ts`). So:

- Clearing site data, a private window closing, or switching device → you **lose the
  ability to edit, start or delete** the quiz. The quiz itself still exists until the
  sweep.
- Every anonymous quiz is **deleted after 30 days** regardless.
- Signing in and claiming it is the only way to keep it.

Suggested copy on My Quizzes (signed out): *"These quizzes are linked to this browser.
If you clear your browser data or switch device you'll lose access to them, and they're
deleted after 30 days. Create a free account to keep them."*

---

## 2. Route audit

Every route in `frontend/src/routes`, with what it does today and a proposal.
**K** Keep · **M** Merge · **H** Hide · **R** Remove (needs both of us) · **I** Investigate.

### Core flow

| Route | What it does today | Auth today | Proposal | Notes |
| --- | --- | --- | --- | --- |
| `/` | Landing. Signed-in visitors are redirected to `/my-quizzes` | open | **K** | Redirect retargeted 2026-09-29; the host link goes to `/my-quizzes` and Create to plain `/create` |
| `/play` | Player join (PIN, nickname) and the whole player game | open | **K** = Join | Fixed 2026-09-29: inline join errors, 2-character nickname minimum with a hint, Home link, Leave, and a "game ended" screen (§4.3) |
| `/explore` | Browse newest public quizzes; `?q=` searches (Meilisearch) | open | **K** = Discover | Change the label to "Discover" and keep the URL. Only `public=True` quizzes appear, and public means world-visible |
| `/search` | 302 to `/explore?q=` | open | **K** (redirect) | Already merged |
| `/create` | Makes a new quiz and opens the editor | open | **K** | Done 2026-09-29: signed out → anonymous quiz, signed in → account quiz. Old `?anon=true` links still work |
| `/edit` | Editor: left rail of questions plus one question card at a time | owner, or anon secret | **K**, redesign | See §4.3 |
| `/view/[quiz_id]` | Quiz home: title, questions, Play, Practice, Download, owner Edit/Delete, anon expiry/claim | open by link | **K**, redesign (#17) | Redesigned 2026-09-28 (see §4.4); browser check still owed |
| `/admin` | Host: lobby → question → results → podium | holder of `game_pin` + `game_id` | **K** | Fixed 2026-09-29: Cancel game in the lobby, End game mid-game, podium Back → `/my-quizzes`, and a Back on the registration-error state (§4.3) |
| `/dashboard` | 302 to `/my-quizzes` | open | **M** into `/my-quizzes` | Merged 2026-09-29 (D1). `/dashboard/files` is a separate route and untouched |
| `/my-quizzes` | Signed out: this browser's quizzes, with expiry. Signed in: the account's quizzes, then this browser's under "On this browser" with Claim | open | **K** = My Quizzes (survivor) | Merged 2026-09-29. Play, Edit and Delete on every row; Analytics and Download on account rows |
| `/overview` | 301 to `/my-quizzes` | open | **K** (redirect) | Retargeted 2026-09-29 |

### Account

| Route | What it does today | Proposal | Notes |
| --- | --- | --- | --- |
| `/account/login` | Two-step login, `returnTo` restricted to this site | **K** | |
| `/account/register` | Registration, links to ToS and privacy | **K** | |
| `/account/password-reset`, `/account/reset-password` | Request a reset / set a new password | **K** | Never confirmed with real mail from the deployed site |
| `/account/resend-verification` | Re-send the confirmation mail | **K** | |
| `/account/settings` | Profile, password, sessions, delete account | **K** = My Account | Remove its two buttons to the avatar editor and the public profile (both deferred) |
| `/account/settings/avatar` | Custom avatar editor | **H** | Custom avatars were deferred in mvp-scope.md |
| `/account/settings/security` | TOTP and backup codes | already hidden | |
| `/account/oauth-error` | Error page for OAuth sign-in | **K** (inert) | The future Azure SSO lands here |
| `/user/[user_id]` | Public profile and that user's quizzes | **H** | Deferred. Linked from settings (the view page's author link was removed 2026-09-28) |

### Secondary features

| Route / feature | What it does today | Proposal | Notes |
| --- | --- | --- | --- |
| `/import` | Kahoot URL, Excel `.xlsx`, or frogQuiz `.cqa` file | **I** → probably **H** from nav | Signed-in only, all three formats. See §3 |
| `/edit/files` | File library: list, rename, delete your uploads | **H** | Reached only from the dashboard's Files button. See §3 |
| `/dashboard/files` | Renders an empty grid of empty `<div>`s | **H**, then **R** | Dead, linked from nowhere. `redesign-status.md` calls it "verified clean" — it is clean because it is empty |
| `/edit/videos` | Video editor, reachable from the uploader's video path | **H** | Video upload is already hidden in the uploader |
| `/results`, `/results/[result_id]` | Saved game results history | **H** | No analytics in MVP. Hide the podium's Save results button with it (decision D4) |
| Analytics (modal on `/dashboard`) | Per-quiz charts from saved results | **H** | Same data source as `/results` |
| `/practice` | Solo run-through of a quiz with no timer, scored like the game | **K** (decision D3) | Rebuilt 2026-09-29 on the game's answer tiles; checked at 390/834/1440 in both themes. Linked from the view page |
| Download (view page and My Quizzes) | Export as Excel | **K** (decision D5) | Rebuilt 2026-09-29 as a shadcn `Dialog`, Excel only. The export now carries CHECK questions, plain-text titles and more than four answers |
| `/remote` | Control a running game from a second device | **H** | Not flag-gated, not redesigned. Linked from a host popover |
| `/docs` and 8 sub-pages | Upstream-style docs | **H** from nav | Keep `tos` and `privacy-policy` (linked from registration) and `attribution` (credit to upstream). Hide `self-host`, `develop`, `roadmap`, `pow`, `import-from-kahoot` |
| GitHub links (navbar, footer) | Link to the repo | **H** | Already a triage candidate in `CLAUDE.md` |

### Already hidden — leave as-is

`/quiztivity/*`, `/controller`, `/account/controllers/*` (flag plus route guard),
`/moderation` (404 in its loader; API gated on an empty `mods` list).

### Navigation today vs. proposed

| | Today | Proposed |
| --- | --- | --- |
| Signed out | Play · Explore · Docs · GitHub · Register · Login | **Discover · My Quizzes · Join** · Sign in |
| Signed in | Play · Explore · Dashboard · Docs · GitHub · Logout | **Discover · My Quizzes · Join** · My Account (menu with Sign out) |
| Dashboard toolbar | Create · Import · Results · Files · Settings | **Create** (plus Import only if D6 keeps it) |

The permanently highlighted Play pill reads as "you are here" on every page, so the
navbar needs a real current-page indicator as well.

**Landed 2026-09-29:** Discover · My Quizzes · Join for everyone, with `aria-current` and
a muted pill on the current page. Signed in adds My Account (a plain link, not yet a
menu) beside Log out. Docs and GitHub are still shown to signed-out visitors: taking a
tab out of the navbar is the joint decision in `CLAUDE.md`, so it waits for François.
The toolbar lost Settings (now My Account in the navbar); Import, Results and Files stay
until D4–D6. Aside: the navbar's Register link only shows when `VITE_REGISTRATION_DISABLED`
is set — inverted, inherited from upstream, and invisible because the proposed navbar
has a single Sign in anyway.

---

## 3. Investigations, with what the code already answers

### Import

- **What exists:** three formats on `/import`, all **signed-in only** (every endpoint
  uses `get_current_user`, and the page redirects signed-out visitors to login):
  - **Kahoot URL** (`create.kahoot.it/details/...`) — `POST /api/v1/quiz/import/{id}`.
    Calls Kahoot's API from our server, so it can break whenever Kahoot changes it.
    Backend tests exist (`test_kahoot_import.py`); they talk to Kahoot live.
  - **Excel `.xlsx`** — `POST /api/v1/quiz/excel-import`, from a template.
  - **frogQuiz `.cqa`** — `POST /api/v1/eximport/`, the round trip of Download.
- **Anonymous users:** cannot import at all.
- **Not checked:** none of the three is in the e2e suite, and nobody has recorded
  importing a real Kahoot through the deployed site.

- [ ] Import one real public Kahoot through the deployed site — not needed while Import is hidden
- [ ] Import the Excel template — not needed while Import is hidden
- [ ] Round-trip a quiz through Download `.cqa` → Import — not needed while Import is hidden
- [x] **D6 decision** — expose Import in MVP? **Hide** — G ☑ F ☐ (2026-09-29). `/import` and its doc page 404; the API stays up

### Files library

- **What it is:** `/edit/files` lists your uploads with rename and delete.
  `/dashboard/files` is an empty placeholder.
- **Quiz media does not depend on it.** The editor uploads images directly through
  `lib/editor/uploader.svelte` → `POST /api/v1/storage/`, which works for anonymous
  users too. The uploader's Library, Video and Pixabay tabs are already hidden.
- **What hiding it costs:** nobody can rename or bulk-delete uploads. The per-user quota
  is about 1 GB (`free_storage_limit`), so nobody will hit it through normal use.
  Deleting a quiz removes its **question** images, but not its cover or background
  image. Deleting an account removes all of that user's files.
- **Conclusion:** safe to hide. Media stays managed inside the quiz, as proposed.

- [x] Hide `/edit/files`, `/dashboard/files` and `/edit/videos`, and remove the dashboard's Files button (2026-09-29, D15)
- [ ] (optional) Make quiz delete also remove `cover_image` / `background_image`, so hiding Files leaks nothing

### Results and analytics

- The podium, per-question answer distribution and standings, and the spreadsheet export
  all work **without** saved results, and without an account.
- `/results` and Analytics read only rows written by the signed-in host's Save results
  button. Hide all three together, or none.

---

## 4. The checklist

Owner column: **G** Gonçalo, **F** François, **G+F** both.

### 4.0 Decisions (settle these first — each one unblocks work below)

| # | Decision | Recommendation | G | F |
| - | --- | --- | - | - |
| D1 | `/my-quizzes` is the surviving URL, and `/dashboard` redirects to it (reverses #18's direction) | Yes — the name matches the label | ☑ | ☐ |
| D2 | Question types in MVP: ABCD only, or ABCD + CHECK | ABCD + CHECK. CHECK works and scores all-or-nothing. **G (2026-09-29): ABCD + CHECK**; the other five are hidden from the type picker | ☑ | ☐ |
| D3 | Practice mode: hide or redesign | Hide the link on the view page. **G (2026-09-28): keep and redesign** | ☑ keep | ☐ |
| D4 | Results history and Analytics: hide, together with the Save results button | Hide all three. **G (2026-09-29): hide all three** | ☑ hide | ☐ |
| D5 | Download: keep (it is the only backup/export) and restyle, or hide | Keep `.cqa` only if D6 keeps Import; otherwise hide. **G (2026-09-28): keep and restyle; (2026-09-29, after D6): Excel only**, `.cqa` hidden until Import returns | ☑ keep, Excel | ☐ |
| D6 | Import: expose in MVP or hide | Decide after the three test imports in §3. **G (2026-09-29): hide**, with its doc page | ☑ hide | ☐ |
| D7 | Editor redesign: continuous Google Forms-style list replaces the rail | Yes, but after everything in 4.1–4.3 ships | ☑ | ☐ |
| D8 | Shared contact address to replace `francois.prevot@frog.co` in the ToS, `CONTACT.md` and `CONTRIBUTING.md` | Needs a real team channel. **G (2026-09-29): leave the placeholder for now**; does not block internal sharing | ☐ | ☐ |
| D9 | User database / login architecture for V1 = the "account is what makes a quiz permanent" model in mvp-scope.md; Azure SSO after V1 | Confirm | ☑ | ☐ |
| D10 | English-only (33 locale files removed) | Confirm. **G (2026-09-29): English-only for the MVP, but keep the i18n machinery** (i18next, `getLocalization`, the backend's language handling); more languages are an MVP2 item (§4.8) | ☑ | ☐ |
| D11 | WebAuthn and ratings endpoints: flag-gate, or accept as live | Flag-gate like QuizTivity. Done 2026-09-29: `ENABLE_WEBAUTHN` gates adding a key (listing, deleting and signing in with an existing key still work, as with TOTP); `ENABLE_RATINGS` gates rating | ☑ | ☐ |
| D12 | View page shows the answer key (correct answers, ORDER sequence, TEXT answers, RANGE bounds) to the quiz's owner only | Yes — a visitor may play it later. Presentation only: the public API still returns the answers | ☑ | ☐ |
| D13 | What "private" means: today anyone with the link can open a private quiz's view page (only the owner can start it) | **G (2026-09-29): relabel it "Unlisted"** — public = in Discover, unlisted = link only. No backend change | ☑ | ☐ |
| D14 | Editor drafts | **G (2026-09-29): autosave to the server.** A half-built quiz saves as a draft, shows a Draft badge on My Quizzes, and can't be started until complete (enforced in `quiz/start`). Red rings and alerts only after the first Save or Start attempt. **Done 2026-09-29**, see §4.5; the draft state is derived from the questions rather than stored | ☑ | ☐ |
| D15 | Hide `/remote`, public profiles (`/user/[id]`), the avatar editor, and the Files library (`/edit/files`, `/dashboard/files`, `/edit/videos`) | **G (2026-09-29): hide all** | ☑ | ☐ |

G's ticks above were given in Claude sessions on 2026-09-28 and 2026-09-29. D12 is already
implemented on the view page, since it is a display choice and reversible in one line; say
so if you disagree, François.

On 2026-09-29 Gonçalo asked for the MVP to be finished that day without waiting on
François's sign-off, including hiding Docs and GitHub. Everything hidden since is
hide-not-delete (route guard plus commented-out nav entry), so any of it can come back in
one edit if François disagrees.

### 4.1 Prove what's already built works on the deployed site (no code)

Nothing has been checked on the real site so far; every check was local. Do these first,
because they may reorder everything else.

- [ ] Host a real game: laptop on a projector, 3+ phones (iOS and Android), signed-in host
- [ ] Same with an anonymous host (`/create` signed out → edit → start → play → podium)
- [ ] Register with a real inbox: confirmation mail arrives, link works, a second click still works
- [ ] Forgot password with a real inbox: mail arrives, reset works, old password rejected
- [ ] Delete a test account that owns a quiz and an uploaded image; confirm both are gone
- [ ] Check `MAIL_*` is set on the production API (`DEPLOY.md` → Email)
- [ ] Run `bash e2e/run.sh` locally and record the result here: ______

> **Running the e2e suite from a VS Code terminal:** with the project venv active,
> `python` is the venv's own interpreter, which has no pipenv, and `run.sh` dies with
> "no pipenv venv". Prefix the system Python:
> `PATH="$LOCALAPPDATA/Programs/Python/Python313:$LOCALAPPDATA/Programs/Python/Python313/Scripts:$PATH" bash e2e/run.sh`.
> Don't run `svelte-check` alongside it — both write `frontend/.svelte-kit` and Vite
> fails with EPERM.

### 4.2 Surfaces and navigation (depends on D1)

- [x] Rename "Dashboard" to "My Quizzes" everywhere (navbar, headings, `en.json`, command palette) — 2026-09-29
- [x] `/my-quizzes` shows the account list when signed in and the browser list when signed out; same actions in both (create, edit, start, delete). Delete confirms in a dialog instead of `confirm()` and no longer reloads the page
- [x] Signed in: offer to claim quizzes this browser made anonymously ("On this browser" section, Claim per row)
- [x] Signed out: the browser-data and 30-day copy from §1, plus a "Create a free account to keep them" CTA
- [x] `/dashboard` and `/overview` redirect to `/my-quizzes`; `/` signed-in redirect too. So do the login default `returnTo` and the register / resend-verification / reset-password redirects
- [x] `/create` works signed out without `?anon=true`
- [x] Navbar: Discover · My Quizzes · Join · (My Account | Sign in); current-page indicator; drop the always-highlighted Play pill. My Account is a link, not a menu, with Log out beside it
- [x] Remove Docs and GitHub from the navbar and footer; keep ToS / Privacy / Attribution in the footer (2026-09-29; also the command palette, and `/docs` plus upstream's doc pages 404)
- [x] Remove Import / Results / Files / Settings from the My Quizzes toolbar (per D4–D6). The toolbar is gone; Analytics went from each row with Results (D4)
- [x] `/account/settings` becomes "My Account" (heading, tab title, navbar, command palette); remove the avatar and public-profile buttons

### 4.3 Close the gaps in the core flow

- [x] **Exit the lobby** — host can cancel a game that hasn't started (end the game server-side, return to My Quizzes). New `end_game` socket event; players see "The host ended the game" and the PIN stops resolving
- [x] **Exit mid-game** — host "End game" with a confirm; goes to the podium or back
- [x] **Player exit** — a Leave button on the player screen, and a "game ended" state if the host ends it. Leave is offered outside live questions only; it frees the nickname and tells the host. New `leave_game` socket event
- [x] **Return** — podium Back goes to `/my-quizzes` for everyone (today anonymous → `/`)
- [x] **A way home from every page in the journey** (Gonçalo, 2026-09-29). Pages that hide the navbar leave you stranded: `/play` shows only "Game PIN" and Submit, with no way back. Audit every route that sets `navbarVisible = false` or renders without the navbar, and give each a home control where leaving makes sense. Exception: mid-game screens, where the exit is the Leave / End game control above rather than a bare link that drops you out of a live game.
  Audited 2026-09-29 — the navbar is hidden on six routes: `/play` (Home link, Leave, game-ended screen), `/admin` (Cancel game, End game, podium Back, and now a Back on the registration-error state that used to be a bare red line), `/create` and `/edit` (the editor's Back, now `/my-quizzes` for everyone). `/remote` and `/edit/videos` were skipped: both are Hide candidates
- [x] Join screen: inline error instead of `alert('Game not found')` / `alert('Unknown error')` — also covers "already started", a taken nickname and being kicked
- [x] Nickname minimum 2 characters, with a hint that says so
- [x] Saving goes to the same place for new and existing quizzes: the quiz's view page, signed in or not (was: edit → dashboard, new → view page)
- [x] Hide the Practice link (D3), `/remote` link, Save results button (D4). Practice is **kept** (D3), so its link stays. `/remote` 404s; its only entry point, a lobby popover, has no emitter left
- [x] Add hidden routes to `DISABLED_ROUTES`: `/remote`, `/results`, `/import`, `/edit/files`, `/dashboard/files`, `/edit/videos`, `/account/settings/avatar`, `/user`, `/docs` and upstream's doc pages. Not `/practice` (kept, D3). Pinned by `frontend/e2e/hidden.e2e.ts`

### 4.4 View page redesign (#17)

The plan is already written up in `BACKLOG.md` → "Design the view page". Code landed
2026-09-28; the browser check at 390/834/1440 in both themes is the last box.

- [x] `fq-section` spacing, `max-w-2xl` column, header as a `Card`
- [x] Questions drawn like the editor canvas (read-only, always open) instead of collapsed full-width bars — changed from the original "shadcn `Collapsible` for questions" at Gonçalo's request
- [x] Delete `lib/collapsible.svelte` — this page was its only consumer
- [x] Anonymous-owner notice as an expandable banner at the top (collapsed: "not saved, deleted in N days"; expanded: explanation and claim / sign up); inline error instead of `alert()`. Delete moved up into the owner actions, behind an `AlertDialog`
- [x] Start as the one primary action; Edit and Delete secondary, owner-only (account or anonymous). Download and Practice left in place pending D5 / D3
- [x] Tokens instead of `bg-white dark:bg-gray-700`, `shadow-blue-500` / `shadow-yellow-500`, `bg-gray-300`
- [x] Remove `console.log(auto_expand…)`; author name stops linking to `/user/[id]`
- [x] Driven in a browser at 390 / 834 / 1440, light and dark, as owner (anonymous and signed in) and as a visitor — 2026-09-29, local stack: no overflow, theme class and ground correct, owner controls and answer key shown to owners only, banner only for the anonymous owner, no raw HTML in titles
- [x] Answer key shown to the owner only (D12)
- [x] Rebuild `DownloadQuiz.svelte` on `Dialog`, Excel only (D5). The Excel export also had three bugs, now fixed and tested (`frogquiz/tests/test_excel_export.py`): it dropped CHECK questions, wrote editor HTML into cells, and a fifth answer overwrote the time limit. Pinned by `frontend/e2e/practice.e2e.ts`
- [x] Redesign `/practice` (D3). Rebuilt rather than restyled: picking any answer threw (an undeclared `i` in every answer loop), so practice had never worked. Same tiles as the game, no timer, ABCD reveals on click, CHECK submits, scored with the game's rules (`lib/practice/score.ts`), a score at the end and Back to quiz on every step. Types the MVP doesn't offer show a notice and a Next. Pinned by `frontend/e2e/practice.e2e.ts`

### 4.5 Editor as drafts, then the redesign (D7)

Drafts first — they are small and help whichever editor we end up with.

- [x] A new or incomplete quiz is a **draft**: nothing is marked red until the first Save. After that the rail, strip, canvas and header point at what is missing, and update live. Over-length counters still show straight away (`lib/editor/validation.svelte.ts`)
- [x] Only block **Start**, not **Save**. The editor **autosaves** to the server 2.5s after typing pauses, once the quiz has a title and a question (`POST /editor/save`, which keeps the edit session open; a new quiz's first save creates it and the URL becomes `/edit?quiz_id=`). Save on an unfinished quiz keeps it as a draft and says what is left; on a finished one it goes to the view page. Back saves first. **No draft column:** a quiz is a draft when a question is unfinished, worked out from its questions by one rule on both sides (`lib/editor/question_complete.ts` and `frogquiz/helpers/completeness.py`), so a flag can never disagree with the quiz. `quiz/start` refuses drafts with a 400 naming the questions; the view page and My Quizzes show a **Draft** badge and disable Play. The server already accepted incomplete quizzes, so `QuizInput` did not need relaxing. Pinned by `e2e/editor.e2e.ts` and `e2e/drafts.e2e.ts`
- [x] Label/placeholder on the description field. It is now optional too: it was required, at least three characters, with nothing saying so
- [x] Fix the question-cap message: the schema caps at 50 but said 32
- [ ] **Redesign:** one scrolling column of question cards, each editing its question and answers in place, "+" between and after cards (Google Forms / Kahoot style), drag-to-reorder kept; the rail becomes an optional outline on wide screens and a drawer below `lg`

### 4.6 Quality and security

- [x] Add code scanning (GitHub CodeQL is free and needs no account; SonarCloud if we want the dashboard) plus Dependabot — `.github/workflows/codeql.yml` (Python + TypeScript, on push, PRs and weekly) and `.github/dependabot.yml` (pip, npm, Actions, Docker)
- [x] Mount `/api/v1/internal/testing` only in test/CI (it returns the full user row, password hash included, and takes `SECRET_KEY` in the query string) — behind `ENABLE_TESTING_ROUTES`, set only in `.env.ci`
- [x] `await` the `check_captcha(...)` call in `join_game` (inert today, a bypass the day captcha is turned on)
- [x] IP lookup: switch `ip-api.com` to HTTPS, or remove the endpoint — off behind `ENABLE_IP_LOOKUP` (nothing calls it, and the provider's free tier is HTTP-only); its test no longer depends on ip-api.com being up
- [x] Decide whether "private" should mean private: `GET /quiz/get/public/{id}` serves any quiz by link today, so private currently means unlisted — relabelled **Unlisted** with a link icon and a one-line explanation in the editor (D13)
- [x] Close issue #13 (deletion fixed by #14; email change deferred by agreement) — closed 2026-09-29, with #18
- [ ] Add `svelte-check` to CI once the ~300 errors in our own code are down (the other ~820 are inside `bits-ui`'s types)

### 4.7 Sign-off play test (the gate before sharing)

Both of us, on the deployed site, after 4.2–4.4 land.

| Flow | Desktop (1440) | Tablet (834) | Phone (390) | Dark mode |
| --- | --- | --- | --- | --- |
| Anonymous: create → edit → start → play → podium → My Quizzes | ☐ | ☐ | ☐ | ☐ |
| Signed in: same, plus claim an anonymous quiz | ☐ | ☐ | ☐ | ☐ |
| Player: join by PIN and by QR, answer, reload mid-game, leave | ☐ | ☐ | ☐ | ☐ |
| Host exits from lobby and mid-game | ☐ | ☐ | ☐ | ☐ |
| Register → confirm → login → reset password → delete account | ☐ | ☐ | ☐ | ☐ |
| Discover: browse, search, open a public quiz, start it | ☐ | ☐ | ☐ | ☐ |

- [ ] No horizontal scroll at any of the three widths (`document.documentElement.scrollWidth > clientWidth`)
- [ ] Closes #19 (visual pass), #16 (modal live check), #3 (MVP1 umbrella)
- [ ] G ☐ F ☐ — agreed it's ready to share

### 4.8 After V1 (not blockers)

- [ ] Azure single sign-on (build on `frogquiz/oauth/`, which is config-gated and deliberately kept)
- [ ] Internal wiki page: tools, alternatives, pros/cons
- [ ] MVP2 features (avatars, rank position, word cloud, etc.) — issue #4 and `BACKLOG.md`
- [ ] More languages (D10). The 33 upstream locale files were removed, but i18next, `getLocalization` and every `$t(...)` call are still in place, so adding a language is a translated `locales/<lang>.json` plus a picker
- [ ] Submit frogQuiz to the internal Use Case Hub

---

## 5. Already done — don't redo

- Account deletion removes the user's quizzes, sessions, API keys and files (#14, audited in #21)
- Registration, verification and password recovery are built and tested in CI (#12, #15, #21); the double-click verify-link bug is fixed (#20)
- Anonymous create / edit / host / delete / claim, and `/my-quizzes` as a browser list
- Host start-game modal rebuilt; Normal vs Old-School removed (game mode fixed to `kahoot`)
- Explore and Search merged into `/explore`
- All 24 bugs from the 18 Sep e2e run fixed (answer races, host takeover, reload scoring, etc.)
- Question-type picker reduced to ABCD + CHECK (backend still has all seven)
- Backend tests run in CI on every backend push; 95 frontend unit tests
- Local full stack without Docker: `bash e2e/run.sh`
