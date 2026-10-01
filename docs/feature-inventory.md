<!--
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

# Feature inventory — the small, odd and half-finished

Every socket event, HTTP route, feature flag and small UI affordance in the app, with
what state it is actually in. Swept 1 Oct 2026.

**State**: `live` reachable and works · `hidden` behind `lib/hidden_routes.ts` or a
backend flag · `orphaned` the code exists and nothing reaches it · `broken` reachable
and does not work.

Claims marked **verified** were reproduced or disproved by hand. The rest are from a
code sweep and are reliable about what the code says, not about what a browser does.

---

## The ones that are actually broken

| What | Where | State |
| --- | --- | --- |
| **Command palette search threw on every hit.** MiniSearch returns the `id` an action was indexed under; four actions were removed, leaving ids 0, 1, 5, 6, 8 in a five-slot array, so `actions[id]` was `undefined` for every search result — an empty list and a `TypeError: ... reading 'args'` per render | `lib/components/commandpalette.svelte:133` | **verified, fixed 1 Oct** |
| **The palette was also upstream's unstyled original** — a black panel with `bg-gray-700` rows and a `#B07156` highlight, laid out with `w-screen h-screen` (both traps `CLAUDE.md` lists) | same file | **verified, fixed 1 Oct** |
| **A refused answer is silent.** The server emits `already_replied` and `question_not_active`; no frontend listener exists for either, so a player who answers twice, or answers after the reveal, sees "Answer locked in" | server `socket_server/__init__.py:394, 406, 422`; no `socket.on` anywhere in `frontend/src` | **verified** — still open |
| **No `disconnect` handler.** A closed tab stays in `game_session:{pin}:players`, so the "everyone has answered" shortcut can never fire again once somebody walks away without pressing Leave. The host waits out the full timer every question | `socket_server/__init__.py` has no disconnect handler | **verified** — still open |
| `routers/results.py:62-84` — the "re-export a saved result" function is **inside a `"""…"""` string literal**, so the route is never registered. Its body also references undefined names | `routers/results.py` | does not exist |
| Moderation pagination is inverted: "Previous Page" does `page+1`, "Next Page" does `page-1` | `routes/moderation/+page.svelte:52-58` | hidden route |
| `avatar.py:52` indexes `hair_color` into `AvatarItemsAsList.hat_color` | `routers/avatar.py` | hidden route |
| Reported as a crash on every `/play` load (`window.hcaptcha` undefined, then `.render` read) — **does not reproduce**: `window.hcaptcha` is an object and `/play` throws nothing | `lib/play/join.svelte:67` | **verified not a bug** |

## Worth a decision

| What | Why it matters |
| --- | --- |
| **`/eximport/excel/{quiz_id}` has no owner filter** (`routers/eximport.py:194`) — any signed-in user can download any quiz by id, answers included. The `.cqa` route has the same gap at `:92`, but it is hidden. This is consistent with "unlisted, not private" (D13), and it is still worth saying out loud | live |
| **`check_captcha` returns `True` when no captcha secret is configured** (`socket_server/helpers.py:23`), so a game with captcha on and no key accepts anybody. Inert today — `start_game.svelte:69` hard-codes `captcha_enabled: 'False'` | inert |
| **`show_solutions` reads the session and the game before checking `session["admin"]`** (`socket_server/__init__.py:461-464`) | minor |
| **Nothing writes `GameResults` rows.** `save_quiz` is behind `SAVE_RESULTS_ENABLED = false`, so the custom-field answers players type only ever leave through the spreadsheet export | by design (D4) |

## Small features that work, and nobody would guess are there

| Feature | How you reach it |
| --- | --- |
| **Custom field** — the host writes one extra prompt ("Team?", "Email?") shown on the join screen; answers land in Redis and become a column in the export | Start-game dialog → Custom field |
| **Randomise answers** per game | Start-game dialog |
| **Hide this question's results** — scores are recorded but the distribution never goes up | Editor → question card → gear → Advanced settings |
| **Kick a player** — every lobby nickname is a button; kicking writes a cookie that refuses that player *that PIN only*, for a day | Lobby → click a nickname |
| **Rejoin after a reload** — a 5-hour cookie carries (sid, username, pin) and re-seats the player on the question currently up | Reload mid-game |
| **Keyboard advance** — Enter or Space runs a state machine that picks the right next action for whatever the host screen is showing | Host screen, any key |
| **Join QR code**, click to fill the projector | Lobby |
| **Owner-only answer key** — a visitor gets ORDER answers alphabetised instead of in the stored order | Any quiz page |
| **Anonymous expiry banner** — days left, and a sign-up offer to keep it | A quiz you made without an account |
| **Moderator rating panel** — seven buttons, reachable only by hand-typing `?mod=true` | `/view/{id}?mod=true` |
| **Command palette** — Ctrl/Cmd+K, `/newquiz {title}` with argument interpolation | Anywhere |
| **Lobby music** | Lobby, bottom left |

## Orphaned — code with nothing pointing at it

**Whole features**: the live-game API (`/api/v1/live/*`, seven routes behind an API key nothing mints), API keys themselves (`POST/GET/DELETE /users/api_keys`), WebAuthn/passkey login (the frontend splices `PASSKEY` out of the offered methods at `account/login/+page.svelte:66`), quiz ratings (`RatingComponent.svelte` is imported by nothing, and `ENABLE_RATINGS` is off), the Pixabay picker and the upload Library (`pixabay_enabled`/`library_enabled` are `false` at every call site), video upload, proof-of-work (`lib/hashcash.ts`, zero importers), the physical-controller code display, `/remote`'s "a game is in the lobby" popover, the stats endpoints, the sitemap, `POST /editor/finish`, `DELETE /users/signout-everywhere`, `POST /results/set_note`, `GET /results/list/{quiz_id}`, the admin user-deletion routes, `/utils/ip-lookup`, the `dark_mode` parameter on the QR endpoint, and the `session_id` the socket emits on connect that nothing listens for.

**Orphaned components**: `lib/dashboard/Analytics.svelte`, `lib/play/end.svelte`, `lib/modals/alert.svelte` (and the `alertModal` store, whose every `.set()` call site is commented out), `lib/files/dashboard.svelte`, `lib/clickOutside.js`, `lib/dashboard/useViewportAction.js`, `lib/editor/slides/types/*`, `lib/view_quiz/Hoverable.svelte`. `lib/play/audio_player.svelte` was one until it was replaced on 1 Oct.

**Orphaned config**: `config.ts`'s `captcha_enabled` export is imported by no file; `routes/create/+page.svelte:33` reads a `create_game` localStorage key nothing ever writes.

## Flags

**Backend** (`frogquiz/config.py`): `enable_box_controller`, `enable_quiztivity`, `enable_totp`, `enable_webauthn`, `enable_ratings`, `enable_testing_routes`, `enable_ip_lookup` — all default `False`. `rate_limit_enabled` and `validate_email_deliverability` default `True`. `registration_disabled`, `skip_email_verification` default `False`. `storage_backend` is required with no default. `mail_configured` is derived: without it registration needs `skip_email_verification` and password recovery is off.

**Frontend** (`lib/config.ts`): `VITE_GOOGLE_AUTH_ENABLED`, `VITE_GITHUB_AUTH_ENABLED`, `VITE_CUSTOM_OAUTH_NAME`, `VITE_REGISTRATION_DISABLED`, `VITE_HCAPTCHA_SITE_KEY`, `VITE_RECAPTCHA_KEY`, `VITE_API_ORIGIN`. All unset by default.

**Hard-coded switches, not env**: `DISABLED_ROUTES` (19 entries) in `lib/hidden_routes.ts`; `SAVE_RESULTS_ENABLED = false`; `library_enabled` / `pixabay_enabled` / `video_upload` all `false` at every uploader call site; `captcha_enabled: 'False'`, `cqcs_enabled: 'False'`, `game_mode: 'kahoot'` in `start_game.svelte`; the question-type allowlist in `AddNewQuestionPopup.svelte`; English-only i18n.

## Hidden but intact

`/remote` (a full second-device controller, with working socket handlers), `/import` (Kahoot URL, Excel, `.cqa`), `/results`, `/edit/files`, `/edit/videos`, `/user/[id]`, `/account/settings/avatar`, `/account/settings/security`, `/quiztivity/*`, `/controller`, `/account/controllers/*`, `/moderation`, and nine `/docs` pages. Each is one line in `lib/hidden_routes.ts`.

The five question types the editor no longer offers — RANGE, TEXT, VOTING, ORDER, SLIDE — still load, play, score and export. Only creation is gated.
