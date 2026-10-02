<!--
SPDX-FileCopyrightText: 2026 François & Gonçalo

SPDX-License-Identifier: MPL-2.0
-->

# Deploying frogQuiz

## What can and cannot go on Netlify

Netlify hosts the **SvelteKit frontend only**. The backend cannot run there: it is a
long-lived FastAPI + socket.io process with an arq worker, Postgres, Redis and
Meilisearch behind it. Netlify Functions are ephemeral and have no WebSocket support,
so gameplay traffic (`/socket.io/*`) cannot pass through Netlify at all.

Two supported layouts:

| Layout                 | Frontend                            | Backend                                                           |
| ---------------------- | ----------------------------------- | ----------------------------------------------------------------- |
| Single host (simplest) | container from `docker-compose.yml` | same compose stack                                                |
| Split                  | Netlify                             | container host (VPS, Fly, Railway) running the same compose stack |

## Option A — everything on one host

1. Copy `.env.example` to `.env` and fill it in. `SITE_ADDRESS` should be your bare
   domain (e.g. `quiz.example.com`) so Caddy provisions a Let's Encrypt certificate;
   point that domain's A record at the host first.
2. `docker compose up -d`. Caddy listens on 80/443, routes `/api/*` and `/socket.io/*`
   to the API and everything else to the frontend. `prestart.sh` runs `alembic upgrade head`.

The `api`, `worker` and `proxy` services pull `ghcr.io/ogfrench/frogquiz-*:master`,
built by this repo's workflows. Push to `master` to publish new images.

## Option B — frontend on Netlify, backend on a container host

Backend first: run Option A on your container host, with `SITE_ADDRESS` set to an
API-only domain (`api.example.com`). Then:

1. In `netlify.toml`, replace `https://api.example.com` in both redirects with that
   domain. REST calls are proxied so the auth cookies stay first-party.
2. In Netlify's environment variables, set:
   - `API_URL` — the same backend base URL. Used server-side by `hooks.server.ts`.
   - `VITE_API_ORIGIN` — the same URL. The browser opens the socket.io connection
     straight to it, bypassing Netlify, because Netlify cannot proxy WebSockets.
3. On the backend, set `CORS_ORIGINS` in `.env` to a JSON list containing the Netlify
   site URL, e.g. `["https://frogquiz.netlify.app"]`. Without it the socket.io server
   rejects the cross-origin handshake.
   Also set `TRUSTED_PROXY_HOPS=2`. There are two proxies in front of the app in this
   setup (Netlify, then Caddy), and the rate limiter keys on the last entry of
   `X-Forwarded-For` -- which with two hops is Netlify's egress address, the same for
   every visitor. Left at 1, the whole user base shares one bucket, and
   `/forgot-password`'s five an hour is five for everyone. The trade-off is that the
   entry it then reads is one the caller could forge by reaching Caddy directly, so
   close the backend to everything but Netlify if you rely on the limiter (the
   per-address limits on the mail endpoints hold either way).
4. Set `ROOT_ADDRESS` to the Netlify site URL (it is what appears in emails and links).

`NETLIFY=true` is set by Netlify during builds, which is what switches
`svelte.config.js` from `adapter-node` to `adapter-netlify`. Local and Docker builds
are unaffected.

Trade-off: this splits the deployment across two providers and puts the socket on a
different origin than the page. Option A is cheaper and has fewer moving parts.

## Free hosting

The stack needs always-on containers, WebSockets and a disk for Meilisearch, which rules
out most free tiers: Railway and Fly have no free plan for persistent services, and
Render's free web services sleep after inactivity, which drops live game sockets.

What is actually free:

| Piece                              | Free option                 | Limit                                  |
| ---------------------------------- | --------------------------- | -------------------------------------- |
| Frontend                           | Netlify                     | 100 GB bandwidth/month                 |
| Postgres                           | Neon                        | 0.5 GB storage, autosuspend            |
| API + worker + Redis + Meilisearch | Oracle Cloud Always Free VM | 4 ARM cores / 24 GB RAM, no time limit |

Oracle's Always Free ARM instance runs this whole compose stack with room to spare, and
the images are all multi-arch. Signup needs a card for verification (not charged) and ARM
capacity is often unavailable in busy regions -- retry or pick another region. If that
fails, a Hetzner CX22 is about EUR 4/month and takes ten minutes.

### Oracle Cloud Always Free, step by step

1. Create the instance: Compute > Instances > Create.
   - Image: **Ubuntu 24.04**. Shape: **VM.Standard.A1.Flex**, 4 OCPUs / 24 GB (the whole
     Always Free ARM allowance). Region: **eu-frankfurt-1**, next to the Neon project.
   - Paste your public SSH key.
   - Show advanced options > Cloud-init script: paste `deploy/oracle-cloud-init.yaml`.
   - "Out of capacity" is the usual failure. Retry, or try another availability domain.
2. Open the ports: Networking > Virtual Cloud Networks > your VCN > the public subnet >
   its security list > Add ingress rules. Source `0.0.0.0/0`, TCP, destination ports 80
   and 443. The cloud-init script has already opened them in the instance firewall.
3. No domain? Use sslip.io: it resolves `134-98-158-173.sslip.io` to `134.98.158.173`,
   and Let's Encrypt issues certificates for it, so `SITE_ADDRESS` can be
   `<dashed-ip>.sslip.io` and Caddy gets real HTTPS with nothing to buy. Otherwise
   point DNS at the instance's public IP (an A record for e.g. `api.yourdomain.com`), then
   set `SITE_ADDRESS` to that name so Caddy can issue a certificate.
4. SSH in and configure:

```bash
ssh ubuntu@<public-ip>
cd /opt/frogquiz
cp .env.example .env && nano .env      # SECRET_KEY, SITE_ADDRESS, ROOT_ADDRESS, mail, CORS_ORIGINS
# using Neon: add DB_URL_OVERRIDE=<neon uri>, then
docker compose -f docker-compose.yml -f docker-compose.neon.yml up -d   api worker redis meilisearch proxy
docker compose logs -f api
```

### Deploying to any Linux VM

```bash
# on the VM (Ubuntu 24.04)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER && newgrp docker

git clone https://github.com/ogfrench/frogQuiz && cd frogQuiz
cp .env.example .env && nano .env          # SECRET_KEY, SITE_ADDRESS, ROOT_ADDRESS, mail
docker compose up -d                       # builds the images on first run

# with Neon instead of the local db container:
#   put the Neon URI in DB_URL_OVERRIDE in .env, then
#   docker compose -f docker-compose.yml -f docker-compose.neon.yml up -d #     api worker redis meilisearch proxy
```

Open ports 80 and 443 in the provider's firewall as well as the OS one -- Oracle's
security list blocks them by default, and Caddy cannot get a certificate without 80.

When the frontend is hosted elsewhere, `CORS_ORIGINS` must list its origin. The
API's own origin is always allowed on top of that, so a browser can talk to the
UI that the API itself serves as well as the remote one.

Keep `MAX_WORKERS: "1"`. The socket.io server holds per-game state in one process; a
second gunicorn worker or a second API replica breaks live games.

## Email

Two things need mail: the confirmation link at registration, and password recovery.
Neither is optional in a way the app can paper over -- without a relay, a forgotten
password can only be fixed in the database.

Set the `MAIL_*` block in `.env` and restart `api` and `worker`:

```
MAIL_SERVER=smtp.resend.com
MAIL_PORT=587
MAIL_SECURITY=starttls        # or ssl for port 465, none for a local relay
MAIL_ADDRESS=noreply@yourdomain
MAIL_FROM_NAME=frogQuiz
MAIL_USERNAME=resend
MAIL_PASSWORD=<api key>
SKIP_EMAIL_VERIFICATION=False
```

`ROOT_ADDRESS` is what goes into the links, so it has to be the public URL people
browse to -- the Netlify site on a split deploy, not the API host. The confirmation
link is `/api/v1/users/verify/...`, which reaches the backend through the Netlify
proxy in `netlify.toml`.

Two things go wrong more often than anything else:

- **`MAIL_ADDRESS` is not a sender the relay will send for.** Every provider checks
  this. Use a verified sender, or an address on a domain with SPF and DKIM set up.
  The symptom is a message the app reports as sent and the provider silently drops
  or bounces.
- **`SKIP_EMAIL_VERIFICATION` is on.** Accounts are then created already verified and
  no confirmation is ever sent. That is a reasonable setting for an internal
  deployment; it is not a mail configuration, and password recovery still needs one.

To run without mail at all, leave the block blank and set
`SKIP_EMAIL_VERIFICATION=True`. Registration then works and recovery does not;
the API says so with a 503 rather than pretending, and the app logs a warning at
startup.

### Testing it for real

The mail path cannot be proved by the test suite: the suite registers
`*@example.com` addresses and never reads an inbox. Somebody has to run it once
against a live relay.

Use **francois.prevot@hotmail.com** as the test recipient (François, 2026-10-02) --
an external address on a provider that is strict about SPF and DKIM, which is the
point: a relay misconfiguration that an internal address would wave through gets
caught here.

Three things to check, in this order:

1. Register a new account with that address. The confirmation mail should arrive,
   the link in it should open the real site (`ROOT_ADDRESS`, not the API host), and
   the account should come out verified.
2. Request a password reset for it. The mail should arrive and the link should let a
   new password be set.
3. Check the spam folder on both. Landing in spam is a pass for the code and a fail
   for the deployment, and it is the most likely outcome on a fresh sender domain.

## Managed Postgres (Neon)

The `db` container can be swapped for Neon when the app host has no persistent disk.
Verified working: `alembic upgrade head` and the running API both accept a Neon URI with
`?sslmode=require` -- psycopg2 and asyncpg each parse it without changes.

```bash
# point api + worker at Neon, keep the rest of the stack local
export DB_URL_OVERRIDE="postgresql://USER:PASSWORD@HOST.eu-central-1.aws.neon.tech/neondb?sslmode=require"
docker compose -f docker-compose.yml -f docker-compose.neon.yml up -d
```

For a real deployment, put the same URI in `DB_URL` and drop the `db` service and its
`depends_on` entries. Pick a Neon region next to the app host -- every query crosses the
network, so a Frankfurt app with a US database pays the round trip on each one.

Neon does not replace the rest: Redis, Meilisearch, the API and the arq worker still need
a host that runs long-lived containers.

## Python version

The Docker image and `Pipfile.lock` are both on Python 3.13. Bumping means changing
`Dockerfile`, `Pipfile`, regenerating `Pipfile.lock` and running the test suite —
`ormar`/`databases`/`sqlalchemy` are the likely breakage.

Backend and frontend lint now run on pull requests. The pytest workflow still does not:
it decodes a base64 `.env` from the `DOTENV` repository secret, which this fork does not
have. Add that secret and uncomment the `pull_request` trigger in
`.github/workflows/pytest.yml` to gate merges on the test suite.
