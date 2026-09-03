# FrogQuiz

Internal Kahoot-style quiz tool, forked from the open-source **ClassQuiz** project (MPL-2.0, original author Marlon W / "Mawoka"). Currently rebranding to a frog-themed identity for internal team use, with room to expand to a wider audience later if it proves useful.

## Project status

- **Scope**: internal tool for now. Don't over-invest in things only public/multi-tenant products need (billing, heavy scalability, public docs) unless asked — but don't actively break the ability to widen scope later either.
- **Stack** (inherited from ClassQuiz, see repo root for details): FastAPI + python-socketio backend (`frogquiz/`), SvelteKit 2/Svelte 5 + TypeScript frontend (`frontend/`), Postgres, Redis, Meilisearch, Alembic migrations.
- **Redesign direction**: moving to a frog-themed visual identity, planned to be built with **shadcn-svelte**, connected via an MCP server. Not set up yet — when this work starts, check what's actually in the repo before assuming shadcn/MCP config exists.

## Feature triage (internal-tool lens)

The app carries a lot of features aimed at a public multi-tenant SaaS. For an internal Kahoot clone, default posture:

- **Hide/disable, don't delete** anything not needed right now (public docs pages, GitHub links in nav/footer, moderation tooling, public OAuth providers beyond what the team actually uses, box-controller/physical-buzzer hardware support, Pixabay integration, hCaptcha/reCAPTCHA, proof-of-work anti-bot challenge, Sentry/Plausible telemetry if unused). Prefer feature flags, route guards, or commenting out nav entries over ripping code out — we may want these back.
- **Search bar**: keep. Useful for finding/sharing quizzes made by other people on the team.
- When asked to "clean up" or "trim" the app, propose a list of hide/disable candidates with rationale and wait for a decision before touching anything — don't remove features unilaterally.
- Remaining known leftover: README Credits section still links to upstream's own donation buttons (Ko-fi/Liberapay) — low priority, flag if touching that file.

## Upstream independence

FrogQuiz should not send data to, or depend at runtime on, servers controlled by the original ClassQuiz maintainer ("Mawoka"). This is separate from MPL-2.0/SPDX attribution (below), which is static legal text, not a network call or data flow.

- Before adding any third-party script, API call, downloadable asset, or contact link, check it isn't pointing at `mawoka.eu` or other upstream-controlled infrastructure.
- Already fixed: `frontend/Dockerfile`'s `API_URL` default (was `https://mawoka.eu`, now points at the internal `api` service), the Plausible analytics script and Sentry error reporting (both removed, were pointing at Mawoka's own instances), the newsletter signup form (removed — it posted visitor emails to `newsletter.mawoka.eu`), the quiz-report mailto, the import-template download link, the email footer link, and `CONTACT.md`/`CONTRIBUTING.md`/ToS contact info (repointed to internal placeholders — see TODOs in those files for the team's real contact channel).
- `docs/attribution`'s credits to real individual upstream contributors and translators were kept — that's legitimate attribution to people, not a data-flow or infrastructure dependency.

## Licensing (MPL-2.0 / REUSE)

- Source files carry `SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)` + `SPDX-License-Identifier: MPL-2.0` headers under the REUSE spec.
- **Never strip or alter existing copyright/license headers.** When substantially modifying a file, add a second `SPDX-FileCopyrightText` line for FrogQuiz contributors rather than replacing the original (see `README.md` for the existing dual-header pattern).
- If a request would require removing/altering these headers, flag it and check with the team rather than doing it silently — MPL-2.0 has real attribution obligations even for internal-only use, and getting this wrong could matter if the tool ever gets shared more widely.

## Changelog

Every time you make a code/config change in this repo (not for pure Q&A or research), append an entry to `CHANGELOG.md` under an `## Unreleased` section at the top, one line per change, in plain past-tense terms a teammate can scan (e.g. "Removed GitHub link from footer nav"). Do this automatically as part of the change, without being asked each time.

## Collaboration workflow

- Both teammates work on a **shared branch** — no heavy PR/branching ceremony for this internal project.
- Quality/safety gate: commits should go through a **Claude review pass using a cheap/fast model** before being considered done, checking for correctness and safety issues (not a full design review). Treat this as the equivalent of a lightweight teammate review, not a blocker for experimentation.
- Since there's no formal PR review, be more conservative by default on risky operations (schema changes, deleting code, touching auth/session logic) — surface them clearly rather than assuming shared context.

## Netlify preview workflow (branch → PR → preview → iterate → merge)

To minimize Netlify token usage and test changes safely:

1. **Create a feature branch** locally: `git checkout -b refactor/your-feature-name`
2. **Commit your changes** to that branch (auto-logs to CHANGELOG.md per our rules)
3. **Push to GitHub**: `git push -u origin refactor/your-feature-name`
4. **Create a PR on your fork** (`ogfrench/frogQuiz`) pointing to `master`, NOT the upstream ClassQuiz repo
   - ⚠️ Common mistake: GitHub may default to `mawoka-myblock/ClassQuiz` — double-check the URL is `github.com/ogfrench/frogQuiz/pull/new/...`
   - This triggers a Netlify preview build automatically
5. **Test the preview** at the deploy URL (linked in PR checks)
6. **Continue editing** if needed: push more commits to the same branch
   - Each additional commit does NOT trigger a new Netlify build (saves tokens)
   - The existing preview URL stays live for all commits on the same branch
7. **When ready**: merge the PR via GitHub UI (one-click). Only merges to `master` trigger production builds.

**Token-saving summary:** Branch commits build zero times. PR creation builds once. PR updates build zero times. Only `master` merges build (for real). This keeps preview testing cheap.

**Why not use shared branch directly:** Each commit to `master` would trigger a production build; feature branches let you iterate cheaply before one final merge.
