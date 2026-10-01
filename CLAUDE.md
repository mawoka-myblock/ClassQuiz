# frogQuiz

Internal Kahoot-style quiz tool, forked from the open-source **ClassQuiz** project (MPL-2.0, original author Marlon W / "Mawoka"). Currently rebranding to a frog-themed identity for internal team use, with room to expand to a wider audience later if it proves useful.

## Project status

- **Scope**: internal tool for now. Don't over-invest in things only public/multi-tenant products need (billing, heavy scalability, public docs) unless asked — but don't actively break the ability to widen scope later either.
- **Stack** (inherited from ClassQuiz, see repo root for details): FastAPI + python-socketio backend (`frogquiz/`), SvelteKit 2/Svelte 5 + TypeScript frontend (`frontend/`), Postgres, Redis, Meilisearch, Alembic migrations.
- **Redesign direction**: a frog-themed visual identity built with **shadcn-svelte** (see below). Done: the theme foundation, login, register, My Account, My Quizzes (`/my-quizzes`, which `/dashboard` now redirects to), the view page, the editor (rebuilt as one column of question cards, 2026-10-01), the join screen, and all four game surfaces (lobby, host question, per-question results, podium). `/explore` works and is headed Discover but its cards are still upstream's. The docs and results-history routes are hidden rather than redesigned. A full visual pass of every route at 390/834/1440 in both themes is in [`docs/audit-2026-10-01.md`](docs/audit-2026-10-01.md).

## Redesign: shadcn-svelte

Config lives in `frontend/components.json`: style `vega`, base colour `zinc`, Lucide icons, Inter. **`--primary` is zinc, not green** — the preset's `green` theme is not in `app.css` and `components.json` carries no `theme` key, so every primary control is black in light mode and near-white in dark. That was checked and kept on 2026-10-01 (MVP.md D17); the doc used to claim the opposite. Components land in `frontend/src/lib/components/ui/`, the `cn` helper in `frontend/src/lib/utils.ts`.

- **Adding components**: `node ./node_modules/shadcn-svelte/dist/index.mjs add <name> -y -o` from `frontend/`. The `-y -o` flags matter — without them the CLI opens a TUI that cannot be driven from a piped stdin, and it will hang.
- **There is no shadcn-svelte MCP server.** The `shadcn-svelte` CLI has no `mcp` command, and the generic shadcn (React) MCP cannot read this registry: it requests an index at `/registry/registry.json` (shadcn-svelte serves `index.json`), and its item schema requires `files[].path` where shadcn-svelte emits `target`. Don't re-litigate this — use the CLI. For docs and usage examples, the Context7 MCP covers shadcn-svelte.
- **Reproducing the config**: preset code `bJNGQT2` encodes all of the above. `node ./node_modules/shadcn-svelte/dist/index.mjs apply --preset bJNGQT2 -y` re-applies tokens and font to `app.css`. Presets are generated with `encodePreset` from `shadcn-svelte/dist/preset/index.mjs` if the choices need to change.
- **`app.css` is merged, not owned.** The CLI preserved the SPDX header, the tippy imports, the `@config '../tailwind.config.cjs'` line (which still supplies the `green-600` brand override) and the legacy `@utility` blocks. Re-running `apply` keeps them; don't hand-replace the file.
- **The canonical base layer is live** — `body` takes `bg-background` and `*` takes `border-border`. Unmigrated routes therefore sit on the token background rather than the old `#d6edc9` green. That was a deliberate call: a grep found zero bare `border` classes, so the only visible effect is the page ground the redesign was replacing anyway.
- **Node toolchain**: pnpm 10 (lockfile is v9). pnpm is not on PATH by default; it is at `%APPDATA%
pm`. The `build` script uses `NODE_ENV=production vite build`, POSIX syntax that fails under cmd.exe — run builds from a POSIX shell.

## Visual identity

The look is deliberately breathy: generous whitespace, a single accent, and one loud element rather than colour everywhere.

- **Wordmark**: `frontend/src/lib/components/Wordmark.svelte` — a rainbow-gradient rounded square plus "frogQuiz" set in Inter. It replaced a Marck Script cursive wordmark. The `.marck-script` class still exists in `app.css` because 14 call sites use it, but it no longer loads a script face; it is now the Inter display treatment (semibold, `-0.03em`). Don't reintroduce a cursive face.
- **The rainbow is spent once.** The frogConvert palette (`#ff6b6b #ffb347 #ffd93d #6bcf7f #4fc3f7 #9775fa #ff6b9d`) lives in the mark, and is reserved for the answer-distribution series. Everything else is zinc neutrals plus `--primary`. Adding a third accent is what makes this look generic.
- **Icons**: Lucide, via `@lucide/svelte`, imported per-icon (`import Sun from '@lucide/svelte/icons/sun'`). The navbar previously carried hand-inlined Heroicons SVGs with `stroke="#000000"`, which were invisible in dark mode. No raw `<svg>` icons in components.
- **Buttons**: `$lib/components/buttons/brown.svelte` and `gray.svelte` are thin wrappers over the shadcn `Button` (primary and secondary). They keep their original prop API so their ~30 call sites work untouched. Use them, or the shadcn `Button` directly — don't hand-roll a button.
- **Base radius** is `0.875rem`, tiered so controls sit tighter than surfaces. frogConvert's own base is `1rem`; blanket-applying it made every control read as a pill.

### Things that keep coming back

Recurring bugs worth checking whenever touching UI, each of which shipped at some point:

- `w-screen` is `100vw`, which **includes the vertical scrollbar**, so it overflows by the scrollbar width on any page that scrolls. Use `w-full` (or `inset-x-0` when fixed).
- Hardcoded `text-black` / `bg-white` / `dark:text-black` disappear in one theme or the other. On the landing page `dark:text-black` made a whole panel read as empty. Use tokens.
- Felte's pristine field value is `undefined`, not `null`. `$errors.field !== null` is therefore always true, which is what put a permanent red ring on every registration field. Use a truthiness check.

## Working on the UI: what this codebase gets wrong repeatedly

Beyond the three in "Things that keep coming back", these have each shipped:

- **A grid item defaults to `min-width: auto`**, so it will not shrink below its
  content's intrinsic width and bursts out of its column. A bare `<input>` reports
  about twenty characters. `min-w-0` belongs on the grid or flex _item_, not only on
  the input inside it.
- **`h-screen` is `100vh`**, which on a phone counts browser chrome that is not
  there, pushing the bottom of a full-height layout below the fold. Use `h-dvh`.
- **`w-full` on a flex child** is `width: 100%` of the container, so it overflows the
  row and shoves its siblings out. Use `flex-1 min-w-0`.
- **A translucent background is fine for a static column and wrong for a drawer.**
  `bg-muted/30` let the whole canvas show through the editor rail once it became an
  overlay.
- **A screen that is not inside `fq-stage` has no vertical rhythm at all.** The host
  question screen was the only game surface missing it, which is why its content sat
  flush against the top of the projector with the bottom half empty.
- **Keying an `{#each}` by index reuses the component that sat at that index.** The
  editor column did, and its cards hold a CKEditor instance that keeps its own copy of
  the text — so deleting question 2 left the open card showing question 2's text over
  question 3's answers. Questions have no id, so identity is minted in `editor.svelte`
  with a `WeakMap`.
- **A button inside a `<form>` with no `type` submits it.** The editor is one form, so
  an `AlertDialog.Trigger` on the delete icon saved the quiz and left for the view page
  instead of asking.

### Responsive baseline

Both halves of a live game are used at once, on different devices: the host on a
projector or laptop, every player on a phone. Neither is the secondary case.

- Check 390, 834 and 1440 before calling a screen done. `document.documentElement.scrollWidth
  > clientWidth` at any of those is a bug, not a nit.
- Side panels collapse to an off-canvas drawer below `lg`, with a scrim, a close
  control inside the panel, and dismissal on selecting something. A fixed `w-72` rail
  leaves about 118px of content on a phone.
- Cap the measure on any editing or reading surface (`max-w-2xl mx-auto` is the one
  in use) rather than letting a form stretch to the panel width.

## Verifying UI changes

Check in a browser, don't assume. The dev server binds IPv6-only — use `http://localhost:3000`, not `127.0.0.1`. Without a backend, `/explore`, `/view/[id]` and `/user/[id]` return 500 and data-driven pages render empty; that is the environment, not a regression — use `KEEP_UP=1 bash e2e/run.sh --list` (below) to get a real one.

Assert on these three, since all three have regressed before:

```js
document.documentElement.classList.contains("dark"); // the class toggle, not the OS media query
document.documentElement.scrollWidth > clientWidth; // the w-screen overflow
getComputedStyle(document.documentElement).backgroundColor; // tokens actually applied
```

The ground is on `html`, not `body`: `app.css` keeps `body` transparent on purpose so it
does not paint over the fixed ambient layer. Checking `body` always reads transparent.

### Running the end-to-end suite

`bash e2e/run.sh` (Git Bash, from the repo root) starts the whole stack locally — a
throwaway Postgres cluster, fakeredis, a portable Meilisearch, the API and Vite — with no
Docker or WSL, runs Playwright against the installed Edge, and tears it all down.
`KEEP_UP=1 bash e2e/run.sh --list` leaves the stack up for manual browser checks at
`http://localhost:3000`, including real live games; `bash e2e/stop.sh` stops it. Specs are
in `frontend/e2e/*.e2e.ts`.

Known bugs are encoded as `test.fail(...)`, so the run is green while they exist and a
test turns red when its bug is fixed — delete the marker then. What each one is, and
what has already been checked and holds up, is in
[`docs/e2e-findings.md`](docs/e2e-findings.md). Read it before touching the socket server.

### Running the frontend suite

`pnpm test` (vitest, no browser needed, about a second). It covers the pieces with
real invariants rather than the ones that are easy to assert:

- the answer palette's contrast, separation, and its documented CVD limitation
- `isQuestionComplete`, including the whitespace-title case that used to pass
- every theme token pairing against WCAG AA, read straight out of `app.css`
- the multiple-answer wire format, which is a contract between three places that do
  not import each other and had already drifted once

Before adding a test, check it can fail: the token guard was verified by reverting
`--muted-foreground` to its old value and watching it report 4.39:1.

### Running the backend suite

The suite is order-dependent and shares state, so a re-run against warm infrastructure
lies to you. Two things bite:

- **Postgres**: the tests are not idempotent. Running them twice without recreating
  the database fails at `test_create_test_user` with a 409, because the user from the
  last run is still there.
- **Redis**: sessions, login challenges and the token denylist live there, not in
  Postgres. Dropping the database without clearing Redis fails the suite from
  `test_password_update` onward with a cascade of 401s that looks exactly like broken
  auth code. It is 40 spurious failures from a warm cache. `run_tests.sh` flushes it
  now; if you are driving pytest directly, `redis-cli flushall` first.

Compare against a baseline on clean infrastructure before concluding you broke
something.

## Feature triage (internal-tool lens)

The app carries a lot of features aimed at a public multi-tenant SaaS. For an internal Kahoot clone, default posture:

- **What has already been cut, and how to turn each thing back on, is written down in [`docs/mvp-scope.md`](docs/mvp-scope.md). Read that before proposing or re-litigating a cut.**
- **Which surfaces have been redesigned and which have not is in [`docs/redesign-status.md`](docs/redesign-status.md).** It also records what "verified" did and did not cover, so nobody has to guess whether a screen was actually looked at.
- **Hide/disable, don't delete** anything not needed right now (public docs pages, GitHub links in nav/footer, moderation tooling, public OAuth providers beyond what the team actually uses, box-controller/physical-buzzer hardware support, Pixabay integration, hCaptcha/reCAPTCHA, proof-of-work anti-bot challenge, Sentry/Plausible telemetry if unused). Prefer feature flags, route guards, or commenting out nav entries over ripping code out — we may want these back.
- **Search bar**: keep. Useful for finding/sharing quizzes made by other people on the team.
- When asked to "clean up" or "trim" the app, propose a list of hide/disable candidates with rationale and wait for a decision before touching anything — don't remove features unilaterally.
- Remaining known leftover: README Credits section still links to upstream's own donation buttons (Ko-fi/Liberapay) — low priority, flag if touching that file.

## If Explore or Search are ever removed for real

**Removing a feature that still exists on master is a joint decision between François and Gonçalo — they are equals, neither overrides the other, and it is never Claude's call.** If a session asks for Explore, Search or any other tab to be removed, note the request and leave the feature in place until both have agreed. Frontend branches are for how things look, not for deciding what the app does.

**Nothing is removed today. Both Explore and Search are live and kept.** This section exists so that if the question comes up again it can be answered with the real cost rather than a guess — it is not a plan to remove them.

**They are now one page.** `/explore` does both jobs — no `?q=` browses the newest
quizzes, `?q=` with three characters or more searches — and `/search` is a 302 into it
that carries the query across. Nothing was removed: the route still resolves, both
`explore_page.*` and `search_page.*` are still used, the backend and Meilisearch are
untouched, and the navbar shows one entry instead of two. The old coupling
(`search-card.svelte` rendering `explore_page.*` strings while showing Search results)
is dissolved rather than fixed, because there is only one page left to render.

The removal surface below is unchanged in substance and still the thing to read before
deleting anything — merging two pages is not deleting a feature, and deleting either
one remains a joint François/Gonçalo decision.

If the team ever does decide to delete either, this is the full surface. Do it in this order and do not stop halfway — a half-removal is what leaves reachable-but-broken routes and live endpoints behind a dead UI.

**Explore**

- `frontend/src/routes/explore/` — the route and its loader.
- `explore_page.*` in `frontend/src/lib/i18n/locales/en.json` (one file now — the other 33 locales were removed; see `docs/mvp-scope.md`). **Only safe once Search is gone too**, or once `search-card.svelte` stops using those keys.
- Entry points: navbar (desktop and mobile), the command palette, and any home-page link.

**Search** (bigger — it reaches the backend and a whole service)

- `frontend/src/routes/search/`, `frontend/src/lib/search-card.svelte`, the navbar link, the command-palette entry.
- `search_page.*` and `explore_page.*` in `en.json`.
- `frogquiz/routers/search.py` — `POST /api/v1/search/` and the GET variant. Unregister it from the router table too, or the endpoint stays live and callable even with no UI.
- **Meilisearch itself**, which is the part people forget. It is wired into `frogquiz/config.py`, `frogquiz/helpers/__init__.py`, `frogquiz/routers/quiz.py`, `frogquiz/routers/editor.py`, `frogquiz/kahoot_importer/import_quiz.py`, and the `meilisearch` service in both `docker-compose.yml` and `docker-compose.dev.yml`. Quiz create/edit/import all write to the index, so those write paths have to be unpicked before the service can go — otherwise the app throws on quiz save, not on search.
- There is a reindex job referenced by the CI workflow; check `.github/workflows/` before deleting the service.

Removing the UI is an afternoon. Removing Meilisearch touches the quiz write path, so treat it as its own change with its own testing, not a tidy-up.

## Upstream independence

frogQuiz should not send data to, or depend at runtime on, servers controlled by the original ClassQuiz maintainer ("Mawoka"). This is separate from MPL-2.0/SPDX attribution (below), which is static legal text, not a network call or data flow.

- Before adding any third-party script, API call, downloadable asset, or contact link, check it isn't pointing at `mawoka.eu` or other upstream-controlled infrastructure.
- Already fixed: `frontend/Dockerfile`'s `API_URL` default (was `https://mawoka.eu`, now points at the internal `api` service), the Plausible analytics script and Sentry error reporting (both removed, were pointing at Mawoka's own instances), the newsletter signup form (removed — it posted visitor emails to `newsletter.mawoka.eu`), the quiz-report mailto, the import-template download link, the email footer link, and `CONTACT.md`/`CONTRIBUTING.md`/ToS contact info (repointed to internal placeholders — see TODOs in those files for the team's real contact channel).
- `docs/attribution`'s credits to real individual upstream contributors and translators are kept — that's legitimate attribution to people, not a data-flow or infrastructure dependency. **But the page used to frame them wrongly:** it was upstream's contributor list run through the ClassQuiz→frogQuiz find-replace, so it told nine named people they had contributed to and translated _frogQuiz_. They contributed to ClassQuiz. The page now says that plainly. If you ever re-run a global rename across this repo, this is the class of thing it breaks — check anything that names a person.
- The same find-replace had produced a fabricated testimonial in `frontend/src/lib/landing/testimonials.svelte`: a real person, a real tweet URL, and quote text edited so an endorsement of ClassQuiz read as one of frogQuiz. It was dead code and is now deleted. Do not reintroduce testimonials that were not given to this project.

## Licensing (MPL-2.0 / REUSE)

- Source files carry `SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)` + `SPDX-License-Identifier: MPL-2.0` headers under the REUSE spec.
- **Never strip or alter existing copyright/license headers.** When substantially modifying a file, add a second `SPDX-FileCopyrightText` line for frogQuiz contributors rather than replacing the original (see `README.md` for the existing dual-header pattern).
- If a request would require removing/altering these headers, flag it and check with the team rather than doing it silently — MPL-2.0 has real attribution obligations even for internal-only use, and getting this wrong could matter if the tool ever gets shared more widely.

## Changelog

Every time you make a code/config change in this repo (not for pure Q&A or research), append an entry to `CHANGELOG.md` under an `## Unreleased` section at the top, one line per change, in plain past-tense terms a teammate can scan (e.g. "Removed GitHub link from footer nav"). Do this automatically as part of the change, without being asked each time.

## Collaboration workflow

- Both teammates work on a **shared branch** — no heavy PR/branching ceremony for this internal project.
- Quality/safety gate: commits should go through a **Claude review pass using a cheap/fast model** before being considered done, checking for correctness and safety issues (not a full design review). Treat this as the equivalent of a lightweight teammate review, not a blocker for experimentation.
- Since there's no formal PR review, be more conservative by default on risky operations (schema changes, deleting code, touching auth/session logic) — surface them clearly rather than assuming shared context.
