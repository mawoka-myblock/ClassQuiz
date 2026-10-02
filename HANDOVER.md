<!--
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

# Handover — `ccr-370df3e4-c44t1l`

For François and Gonçalo, 2 October 2026. Read this first; everything else is linked from
here.

**State: green and ready to merge.** 45 commits, 107 files, roughly +7400 / −2500 against
`master`.

| Suite | Result |
| --- | --- |
| e2e | **127 passed**, 10.0 min |
| Backend | **147 passed**, 1 skipped |
| Unit | **126 passed** |
| `flake8 .` | 0 |
| `eslint .` | 0 errors |

---

## 1. Do these three things, in this order

Nothing else on this list has a deadline. These do.

### A. The Oracle VM, before 31 October — 15 minutes, free

Oracle **halved** the Always Free ARM allowance, with no announcement. It is now **2 OCPU
/ 12 GB**; `DEPLOY.md` used to tell you to build 4/24 and called that "the whole
allowance". An over-allowance tenancy is not trimmed to fit — **every A1 instance in it is
disabled and then deleted**.

The site is up today, which proves nothing: the 30-day grace keeps over-limit resources
running right up to the cliff.

1. Oracle console → Compute → Instances → check the shape. If it says 4 OCPU / 24 GB,
   **Edit shape → 2 OCPU / 12 GB**. It reboots but keeps the IP and the disk. Do it when
   no game is live.
2. Copy `uploads/` and `.env` off the box. **Uploaded quiz images exist only on that
   disk** — `STORAGE_BACKEND=local`, no S3, no backup job. If the instance goes, every
   quiz image goes with it while the quiz text survives pointing at nothing.

Full analysis, verified against Oracle's own documentation, with a dated checklist:
**issue #22**.

### B. Prove mail works on the deployed site — 10 minutes

Set `MAIL_*` on the production API and run register → confirm → reset by hand, to
**francois.prevot@hotmail.com**. Steps are in `DEPLOY.md` under "Testing it for real".

The code path is now automated end to end (see §3), including the parts that only exist
inside the email. What automation cannot prove is that a real provider accepts and
delivers it. Check the spam folder on both messages — landing in spam is a pass for the
code and a fail for the deployment, and it is the likely outcome on a fresh sender domain.

### C. Confirm the `worker` container runs in production — 2 minutes

`docker compose ps` on the VM. Without it, the 30-day deletion that the anonymous-quiz
notice promises every user is not actually happening.

---

## 2. What changed, in one paragraph each

**Uploads got real limits.** There was no server-side cap at all: the route passed
`size=0` into storage, and the browser's cap was not applied either because `restrictions`
is an Uppy *Core* option that was being handed to the Dashboard plugin. Now 5 MB per image
and 1 GiB per account, enforced at Caddy, on `Content-Length`, and on the counted bytes.
Deleting an image gives the space back — it never did, so the quota was a lifetime counter
and enforcing it would have locked people out permanently. Deleting a quiz now frees its
images, including cover and background, which a stale regex had silently never done.
[`docs/uploads.md`](docs/uploads.md)

**Live games stopped breaking in three ways.** A closed laptop used to freeze the game for
everyone, because there was no socket `disconnect` handler and the closed tab stayed in
the count that "everyone has answered" is measured against. A refused answer told the
player "Answer locked in" because `question_not_active` had no listener anywhere. And
`captcha_enabled` defaulted to *true* on `/quiz/start`, where it raised an `AttributeError`
out of `join_game`.

**Results are the owner's** (D18, François's call). The view page hid correct answers from
a non-owner while the Download button beside it handed over a spreadsheet containing them,
so any signed-in teammate could read the answers to a quiz they were about to play.

**The host decides what players see on their phones** (D16, "make it like Kahoot"). A
switch in the start modal, off by default — shapes only, question on your screen — exactly
as Kahoot does, which ships the same setting free. Turn it on for a call. Both render
paths already existed; the modal was simply hardcoding one of them.

**The join screen** no longer pre-fills a fake PIN, states the digit count in words, shows
an inert rather than broken-looking Submit while you type, sits in the upper third on a
laptop instead of floating mid-void, and no longer lets a long quiz title swamp the "You're
in" confirmation.

**Hostile input — the app was attacked on purpose, not just exercised.** Three passes, each
a real finding closed with a test that fails against the old code:

- **Unbounded text.** `ormar.Text()` had no length limit, so a 5000-character title saved
  intact, and a 272-character word with no spaces overflowed the player's lobby by 6611 px
  and the host's screen by 7736 px. Now bounded (title 100, description 500, question 250,
  answer 100, measured on visible text), with `wrap-anywhere` at every render site because
  a quiz saved before the bounds is never revalidated.
- **A decompression bomb.** A 20000×20000 PNG of one colour is under 400 KiB — inside the
  5 MB byte cap — and ~1.6 GB as a bitmap in every browser that draws it. The server never
  decodes an image, so the clients (phones, projector) are what fall over. Now rejected by
  a header-only dimension read (no decode, no dependency) at 8000 px per side.
- **Quiz shape, and editor/server drift.** Questions had no bound (5000 accepted → now a
  1000 DoS ceiling, with the tested 200/500 scale contract preserved), and the editor was
  looser than the server on answers (16 vs 10), question length (299 vs 250) and the timer
  (unbounded vs 999) — so a user could build a quiz the server then refused. The six
  correctness limits are pinned editor == server by a test that reads both.

What held up: the nickname bound (50, control chars stripped), the server's timer bounds,
and the answer/timer grids at phone and projector width. One known gap is written down in
`docs/uploads.md`: the uploader's own browser still decodes a true square bomb in Uppy's
Compressor before the server sees it, hanging only the uploader's own tab — a follow-up.

Everything else is in [`CHANGELOG.md`](CHANGELOG.md).

---

## 3. The test suites, and why they are worth trusting

115 → **127 e2e tests**, and six of the new ones are *user journeys* rather than feature
tests. The distinction matters: the existing suite was organised by mechanism — sockets,
editor, uploads, exits — and was thorough at it, but a journey fails for a different
reason. Not "this control is wrong" but **"you cannot get from here to there."**

| Journey | What it walks |
| --- | --- |
| `journey-recovery` | Sign up, forget, request a reset, **read the real email**, follow the link, set a new password; old one refused, link dead the second time |
| `journey-first-game` | Land on `/`, Create with no account, write two questions, host, two phones join, play, podium, back to My Quizzes |
| `journey-teammate` | Owner publishes; a teammate finds it in Discover, cannot read which answer is right or download the sheet, but can run it |
| `journey-remote-call` | A host with nobody in the room runs a whole game on everyone's phones |
| `journey-returning-host` | Log in, find last month's quiz, change it, run it again |
| `journey-player-phone` | One phone, the whole arc: join, answer, be told, wait, answer, podium, out |

The unlock for the first one is `e2e/mailsink.py` — a 90-line SMTP server, no new
dependency — because `/forgot-password` answers 503 without a relay, so **password
recovery could not be tested at all** before today. It is the one journey `MVP.md` calls a
must-do before sharing.

**What the journeys found is the honest part: every first-run failure was the test's
assumption, not a product bug.** Nine of them. The app was right every time. That is the
useful result — a journey encodes what a *user* expects, and where that disagreed with the
app, the app won. The table of all nine is in
[`docs/session-2026-10-02.md`](docs/session-2026-10-02.md) §4.

---

## 4. Two open test failures, deliberately not explained

`editor.e2e.ts › build a quiz by hand` and `game-reload.e2e.ts › a player can reload
twice`. One occurrence each across six full runs; both pass in isolation (10/10 and 3/3);
the suite has since gone 127/127 twice.

They share a symptom — the player does not get the question — and they are recorded
together in `TODO.md` **with an explicit instruction not to assume one cause**. Earlier in
this session I attributed one of them to a known race, said it was fixed, then measured it
and found the unfixed code passed 10/10. The retraction is in the git history. Do not
repeat it.

---

## 5. Decisions

**Nothing in `MVP.md` §4.0 is waiting on anybody.** François signed D1 and D3–D15 on 2
Oct; D2 and D16 he answered with "like Kahoot"; D8, D9, D17 and D18 are his. Each row
records what was decided and why.

Two judgement calls left open on purpose, neither blocking:

- **The README still links to Mawoka's Ko-fi and Liberapay.** `CLAUDE.md` lists it as a
  leftover, but the same file says credits to real upstream people are kept because they
  are attribution, not a data-flow dependency — and a donation link is static text, not a
  call to his servers. Removing credit is not Claude's call, so it stands. Decide whether
  an internal company README should solicit donations for a third party.
- **SonarQube** is untouched, per François. The nearer neighbour is `svelte-check` in CI:
  229 errors in our own code, 81 of them in five files, three of which are editor parts
  for question types the MVP does not offer — so it is smaller than the number looks.

---

## 6. Where to look

| File | What it holds |
| --- | --- |
| [`TODO.md`](TODO.md) | Running state. Start here for what is done and what is not |
| [`MVP.md`](MVP.md) | The plan and every decision, with both signatures |
| [`docs/session-2026-10-02.md`](docs/session-2026-10-02.md) | This session in full, **including what I got wrong** |
| [`CHANGELOG.md`](CHANGELOG.md) | Every change, newest first |
| [`docs/uploads.md`](docs/uploads.md) | Limits, where each is enforced, and why there is no file manager |
| [`docs/e2e-findings.md`](docs/e2e-findings.md) | Read before touching the socket server |
| [`DEPLOY.md`](DEPLOY.md) | Deployment, the corrected Oracle sizing, and the mail test |

## 7. Running it

```bash
bash e2e/run.sh                      # whole stack + 127 e2e tests, no Docker needed
KEEP_UP=1 bash e2e/run.sh --list     # leave it up at localhost:3000 to click around
bash e2e/stop.sh                     # stop it
cd frontend && pnpm test             # 126 unit tests, about a second
```

The backend suite needs a Python env (`pipenv sync --dev`, or point `E2E_VENV` at one) and
infrastructure; `run_tests.sh` wants Docker or Podman. It is order-dependent and shares
state, so always run it against a fresh database **and** a flushed Redis — a warm cache
produces about 40 spurious 401s that look exactly like broken auth.
