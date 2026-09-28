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
| `/` | Landing. Signed-in visitors are redirected to `/dashboard` | open | **K** | Redirect target becomes `/my-quizzes`. Landing links to Create, My Quizzes and Join |
| `/play` | Player join (PIN, nickname) and the whole player game | open | **K** = Join | Native `alert('Game not found')`; 4-character nickname minimum with no message; no way to leave |
| `/explore` | Browse newest public quizzes; `?q=` searches (Meilisearch) | open | **K** = Discover | Change the label to "Discover" and keep the URL. Only `public=True` quizzes appear, and public means world-visible |
| `/search` | 302 to `/explore?q=` | open | **K** (redirect) | Already merged |
| `/create` | Makes a new quiz and opens the editor | signed-in, or `?anon=true` | **K** | Drop the `?anon=true` distinction: signed out → anonymous quiz, signed in → account quiz. Today, plain `/create` sends a signed-out user to the login page |
| `/edit` | Editor: left rail of questions plus one question card at a time | owner, or anon secret | **K**, redesign | See §4.3 |
| `/view/[quiz_id]` | Quiz home: title, questions, Play, Practice, Download, anon expiry/claim/delete | open by link | **K**, redesign (#17) | Still pre-redesign: `bg-white`, blue/yellow shadows, `alert()`, `console.log`, old collapsible |
| `/admin` | Host: lobby → question → results → podium | holder of `game_pin` + `game_id` | **K** | The only exit is Back on the podium (anonymous → `/`). No exit from the lobby or mid-game |
| `/dashboard` | Signed-in quiz list: start, edit, view, analytics, download, delete; buttons to Import, Results, Files, Settings | signed-in (else 302 to login) | **M** into `/my-quizzes` | Make `/dashboard` a 302 to `/my-quizzes`. This reverses the direction #18 proposed — see decision D1 |
| `/my-quizzes` | Signed-out list built from this browser's secrets, with expiry | open | **K** = My Quizzes (survivor) | Gains the signed-in state from `/dashboard` |
| `/overview` | 301 to `/dashboard` | open | **K** (redirect) | Retarget to `/my-quizzes` |

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
| `/user/[user_id]` | Public profile and that user's quizzes | **H** | Deferred. Linked from the view page's author name and from settings |

### Secondary features

| Route / feature | What it does today | Proposal | Notes |
| --- | --- | --- | --- |
| `/import` | Kahoot URL, Excel `.xlsx`, or frogQuiz `.cqa` file | **I** → probably **H** from nav | Signed-in only, all three formats. See §3 |
| `/edit/files` | File library: list, rename, delete your uploads | **H** | Reached only from the dashboard's Files button. See §3 |
| `/dashboard/files` | Renders an empty grid of empty `<div>`s | **H**, then **R** | Dead, linked from nowhere. `redesign-status.md` calls it "verified clean" — it is clean because it is empty |
| `/edit/videos` | Video editor, reachable from the uploader's video path | **H** | Video upload is already hidden in the uploader |
| `/results`, `/results/[result_id]` | Saved game results history | **H** | No analytics in MVP. Hide the podium's Save results button with it (decision D4) |
| Analytics (modal on `/dashboard`) | Per-quiz charts from saved results | **H** | Same data source as `/results` |
| `/practice` | Solo run-through of a quiz with no timer or scoring | **H** (decision D3) | Pre-redesign (raw SVGs, `bg-white`, `text-black`, absolute `80vh` panels). Linked from the view page |
| Download (view page and dashboard) | Export as `.cqa` (re-importable) or Excel | **I** (decision D5) | Modal is `w-1/3` (about 130px on a phone), `w-screen h-screen`, `bg-white`. Disabled for anonymous users with no explanation |
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

- [ ] Import one real public Kahoot through the deployed site
- [ ] Import the Excel template
- [ ] Round-trip a quiz through Download `.cqa` → Import
- [ ] **D6 decision** — expose Import in MVP? (keep as a secondary action on My Quizzes, signed-in only / hide) — G ☐ F ☐

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

- [ ] Hide `/edit/files`, `/dashboard/files` and `/edit/videos`, and remove the dashboard's Files button
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
| D1 | `/my-quizzes` is the surviving URL, and `/dashboard` redirects to it (reverses #18's direction) | Yes — the name matches the label | ☐ | ☐ |
| D2 | Question types in MVP: ABCD only, or ABCD + CHECK | ABCD + CHECK. CHECK works and scores all-or-nothing | ☐ | ☐ |
| D3 | Practice mode: hide or redesign | Hide the link on the view page | ☐ | ☐ |
| D4 | Results history and Analytics: hide, together with the Save results button | Hide all three | ☐ | ☐ |
| D5 | Download: keep (it is the only backup/export) and restyle, or hide | Keep `.cqa` only if D6 keeps Import; otherwise hide | ☐ | ☐ |
| D6 | Import: expose in MVP or hide | Decide after the three test imports in §3 | ☐ | ☐ |
| D7 | Editor redesign: continuous Google Forms-style list replaces the rail | Yes, but after everything in 4.1–4.3 ships | ☐ | ☐ |
| D8 | Shared contact address to replace `francois.prevot@frog.co` in the ToS, `CONTACT.md` and `CONTRIBUTING.md` | Needs a real team channel | ☐ | ☐ |
| D9 | User database / login architecture for V1 = the "account is what makes a quiz permanent" model in mvp-scope.md; Azure SSO after V1 | Confirm | ☐ | ☐ |
| D10 | English-only (33 locale files removed) | Confirm | ☐ | ☐ |
| D11 | WebAuthn and ratings endpoints: flag-gate, or accept as live | Flag-gate like QuizTivity | ☐ | ☐ |

### 4.1 Prove what's already built works on the deployed site (no code)

Nothing has been checked on the real site so far; every check was local. Do these first,
because they may reorder everything else.

- [ ] Host a real game: laptop on a projector, 3+ phones (iOS and Android), signed-in host
- [ ] Same with an anonymous host (`/create?anon=true` → edit → start → play → podium)
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

- [ ] Rename "Dashboard" to "My Quizzes" everywhere (navbar, headings, `en.json`)
- [ ] `/my-quizzes` shows the account list when signed in and the browser list when signed out; same actions in both (create, edit, start, delete)
- [ ] Signed in: offer to claim quizzes this browser made anonymously
- [ ] Signed out: the browser-data and 30-day copy from §1, plus a "Create an account to keep them" CTA
- [ ] `/dashboard` and `/overview` redirect to `/my-quizzes`; `/` signed-in redirect too
- [ ] `/create` works signed out without `?anon=true`
- [ ] Navbar: Discover · My Quizzes · Join · (My Account | Sign in); current-page indicator; drop the always-highlighted Play pill
- [ ] Remove Docs and GitHub from the navbar and footer; keep ToS / Privacy / Attribution in the footer
- [ ] Remove Import / Results / Files / Settings from the My Quizzes toolbar (per D4–D6)
- [ ] `/account/settings` becomes "My Account"; remove the avatar and public-profile buttons

### 4.3 Close the gaps in the core flow

- [ ] **Exit the lobby** — host can cancel a game that hasn't started (end the game server-side, return to My Quizzes)
- [ ] **Exit mid-game** — host "End game" with a confirm; goes to the podium or back
- [ ] **Player exit** — a Leave button on the player screen, and a "game ended" state if the host ends it
- [ ] **Return** — podium Back goes to `/my-quizzes` for everyone (today anonymous → `/`)
- [ ] Join screen: inline error instead of `alert('Game not found')` / `alert('Unknown error')`
- [ ] Nickname minimum 2 characters, or say why the button is disabled
- [ ] Saving goes to the same place for new and existing quizzes (today: edit → dashboard, new → view page)
- [ ] Hide the Practice link (D3), `/remote` link, Save results button (D4)
- [ ] Add hidden routes to `DISABLED_ROUTES`: `/practice`, `/remote`, `/results`, `/edit/files`, `/dashboard/files`, `/edit/videos`, `/account/settings/avatar`, `/user` (adjust to decisions)

### 4.4 View page redesign (#17)

The plan is already written up in `BACKLOG.md` → "Design the view page".

- [ ] `fq-section` shell, `max-w-2xl` column, header as a `Card`
- [ ] shadcn `Collapsible` for questions; drop `lib/collapsible.svelte` if nothing else uses it
- [ ] Anonymous-owner panel (expiry, claim, delete) as its own `Card`; inline error instead of `alert()`
- [ ] Start as the one primary action; Edit and Delete secondary; Download per D5
- [ ] Tokens instead of `bg-white dark:bg-gray-700`, `shadow-blue-500` / `shadow-yellow-500`, `bg-gray-300`
- [ ] Remove `console.log(auto_expand…)`; author name stops linking to `/user/[id]`
- [ ] If Download stays: rebuild `DownloadQuiz.svelte` on `Dialog` (today `w-1/3`, `w-screen h-screen`, `bg-white`)

### 4.5 Editor as drafts, then the redesign (D7)

Drafts first — they are small and help whichever editor we end up with.

- [ ] A new or incomplete quiz is a **draft**: no red rings on untouched empty fields; show "N questions incomplete" as information, not error
- [ ] Only block **Start**, not **Save**, on incomplete questions (today Save is blocked, so a half-built quiz can't be kept). **Needs a backend change too:** `QuizInput` rejects a quiz with no questions or a question with no answers (the M5/M6 fixes). Either add a draft flag that relaxes validation on save and enforces it in `quiz/start`, or keep drafts client-side until they're valid
- [ ] Label/placeholder on the description field (today an unexplained red box)
- [ ] Fix the question-cap message: the schema caps at 50 but says 32 (`lib/yupSchemas.ts:121`)
- [ ] **Redesign:** one scrolling column of question cards, each editing its question and answers in place, "+" between and after cards (Google Forms / Kahoot style), drag-to-reorder kept; the rail becomes an optional outline on wide screens and a drawer below `lg`

### 4.6 Quality and security

- [ ] Add code scanning (GitHub CodeQL is free and needs no account; SonarCloud if we want the dashboard) plus Dependabot
- [ ] Mount `/api/v1/internal/testing` only in test/CI (it returns the full user row, password hash included, and takes `SECRET_KEY` in the query string)
- [ ] `await` the `check_captcha(...)` call in `join_game` (inert today, a bypass the day captcha is turned on)
- [ ] IP lookup: switch `ip-api.com` to HTTPS, or remove the endpoint
- [ ] Decide whether "private" should mean private: `GET /quiz/get/public/{id}` serves any quiz by link today, so private currently means unlisted
- [ ] Close issue #13 (deletion fixed by #14; email change deferred by agreement)
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
