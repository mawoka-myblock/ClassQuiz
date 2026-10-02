<!--
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

# Uploads: what we accept, how big, and why there is no file manager

Decided 2026-10-01. The short version: **a quiz owns its images, nobody manages a media
library, and every upload has a ceiling the server enforces.**

## No file manager

Upstream shipped one — `/edit/files` and `/dashboard/files`, backed by
`GET /api/v1/storage/list`, plus a "Library" tab and a Pixabay search in the editor's
upload dialog. For a team quiz tool that is a second thing to learn and a second place
for state to rot: you pick an image for a question, and that is the whole job.

So the posture is **a picture belongs to the question it is on**. All four entry points
are off:

| Surface | How it is off |
| --- | --- |
| `/edit/files`, `/dashboard/files` | `DISABLED_ROUTES` in `frontend/src/lib/hidden_routes.ts` |
| Library tab in the upload dialog | `library_enabled={false}` at every `uploader.svelte` call site |
| Pixabay tab | `pixabay_enabled={false}` at every call site, and `pixabay_api_key` is unset |
| Video upload (`/edit/videos`) | `DISABLED_ROUTES`, `video_upload={false}`, and `enable_video_upload: bool = False` |

Nothing is deleted — `GET /api/v1/storage/list` and `lib/files/dashboard.svelte` are
still there — so this is four lines to reverse if the team ever wants a library. See
[`mvp-scope.md`](mvp-scope.md) for the general hide-don't-delete rule.

### Removing an image, and getting the space back

The editor's own X on a question image is how a person manages the file that's there —
that is the whole affordance, and it is enough. What was missing is that it did not
actually free anything:

- **`storage_used` was only ever incremented.** The `calculate_hash` worker job added each
  upload's size and *nothing anywhere subtracted it* — not the delete endpoint, not the
  quiz-update job, not account deletion. So the number was a lifetime upload counter, not
  usage, and the quota built on it was a lifetime cap. Swap a cover image enough times and
  you are locked out for good with nothing to reclaim. Harmless while the quota went
  unenforced; a real lockout once it was.
- `DELETE /api/v1/storage/meta/{file_id}` now releases the file's bytes
  (`release_storage_quota` in `routers/storage.py`), clamped at zero because the column
  declares `minimum=0` and every row predating the size fix stores 0.
- Taking an image off a question used to only *unlink* the relation, leaving the file in
  storage for good. `quiz_update` in `worker/storage.py` now deletes it once nothing points
  at it and gives back its bytes. Reference-counted first: images are many-to-many with
  quizzes, so a duplicated quiz shares them and deleting on the first unlink would pull the
  picture out from under the other one. Soft-deleted (`deleted_at`) the way the endpoint
  does, so an id still written into some other quiz's JSON resolves to a 404 rather than a
  dangling reference.
- **Deleting a quiz did not free its images either, and nor did the 30-day anonymous
  sweep.** Both went through `collect_quiz_image_keys`, whose regex was
  `^.*/(.{36}--.{36})$` — a shape that only ever described upstream's old double-key
  form. A modern upload stores the bare `StorageItem` UUID that `POST /api/v1/storage/`
  returns, with no slash and no `--`, so the regex **matched nothing**: every image of
  every deleted quiz stayed in storage permanently, still charged to its owner. For
  anonymous quizzes that is unbounded growth from people who never come back. Both paths
  now use `release_quiz_images`, which also covers `cover_image` and `background_image`
  (the old helper deliberately skipped them, defensible while nothing was freed at all).
  `collect_quiz_image_keys` is deleted rather than left as a function that silently
  matches nothing.
- The orphan path runs in the worker, so it needs the `worker` container (already an open
  item in [`../TODO.md`](../TODO.md)). The explicit delete runs in the request path and does
  not.

`DELETE /api/v1/users/me` takes a leaver's files with it.

**How the decrement is verified.** No test in this suite can reach the database — the
`TestClient` runs its own event loop, which is why the one attempt at
`User.objects.get(...)` failed with "attached to a different loop" — and a write route to
bill a user would be test-only code in a production app. So `test_deleting_a_file_releases_its_bytes`
covers the reachable half: the row records its size, the delete answers 200, the release is
clamped at zero rather than raising on the `minimum=0` column, and a second delete 404s so a
release can never apply twice. The decrement itself is verified against a live stack:

```
billed:   {"limit":1073741824,"limit_reached":false,"used":4096}
delete:   200
released: {"limit":1073741824,"limit_reached":false,"used":0}
```

Run it with `KEEP_UP=1 bash e2e/run.sh --list`, then register and log in a user, upload a
file, add its size to `users.storage_used` by hand (that is the worker's job and the worker
is not running), delete it and read `GET /api/v1/storage/limit` either side. **Restart the
API first if you have just edited `frogquiz/`** — `run.sh` starts uvicorn without
`--reload`, and this check silently reported no decrement at all until the stack was
restarted. Compare the process start time against the file mtime.

## What is accepted

`upload_limits()` in `frogquiz/config.py` is the single table. "Is this type allowed" and
"how big may it be" are the same lookup, so they cannot disagree.

| Type | Ceiling | Setting |
| --- | --- | --- |
| `image/png`, `image/jpeg`, `image/gif`, `image/webp` | 5 MB | `max_image_upload_size` |
| `video/mp4` | 25 MB, **and off** | `max_video_upload_size`, `enable_video_upload` |
| Per account, all files | 1 GiB | `free_storage_limit` |

`image/svg+xml` is not accepted and should not be: an SVG is a script-injection vector
and nothing in a quiz needs one.

Turning video on takes a third change nobody expects: Caddy's `max_size` is 6 MB, so a
25 MB video would be refused at the edge before the API ever sees it. Flip
`enable_video_upload`, unhide `/edit/videos`, **and** raise `max_size` above
`max_video_upload_size`.

**Why 5 MB.** It covers a photo straight off a phone — a 12-megapixel JPEG is usually
3–5 MB — which is far more than a question image needs on a projector, and the editor
runs Uppy's Compressor at quality 0.6 before it uploads anyway. Kahoot allows 50 MB for
a question image but only 5 MB for a cover
([their docs](https://support.kahoot.com/hc/en-us/articles/115002815387-Kahoot-images-How-to-use-images-and-GIFs)),
so this is not a tighter rule than people are used to. Raise `max_image_upload_size` if
somebody has a real case, and raise the Caddy `max_size` with it.

**Why 1 GiB per account.** A quiz with a cover and an image on every question is a few
megabytes, so this is dozens of quizzes per person: the ceiling is there to stop one
account filling the volume, not to ration normal use. It was 256 MiB for a day, which
was sized for a free Postgres row count rather than for the disk the files actually sit
on. Before raising it further, check the host's own volume — on the Oracle Always Free
VM the block volume is the real limit, not this number.

## How it is enforced

Three layers, because each catches what the others cannot:

1. **Caddy**, `request_body @upload { max_size 6MB }` scoped to `/api/v1/storage/*` in
   both `Caddyfile` and `Caddyfile-docker`. Stops it at the edge. Scoped with a matcher
   so a large quiz JSON save is unaffected. Keep it above `max_image_upload_size`.
2. **`request_size_guard`** in `frogquiz/__init__.py` — rejects on `Content-Length`
   before the body is read. This is the one that matters for cost: Starlette spools a
   multipart part past 1 MB to a temp file, so without it a 2 GB upload is 2 GB written
   to disk before any of our code runs. It allows 64 KiB of slack for the multipart
   framing, so it is deliberately loose; the route is the precise check.
3. **The routes themselves** — `POST /api/v1/storage/` checks the counted bytes
   (`UploadFile.size`, falling back to seeking the spooled file), and
   `POST /api/v1/storage/raw` counts chunks as it streams and aborts mid-transfer. Both
   also check the account quota *including the file in hand*, so the last upload before
   the quota cannot be an arbitrarily large one. 413 for too large, 422 for an
   unaccepted type or an empty file, 409 for the quota.

The browser gets the same numbers from **`GET /api/v1/storage/limits`**, which
`uploader.svelte` fetches on mount and feeds to Uppy's `restrictions`. That is a
convenience, not a control: it tells someone their file is too big before they wait for
the transfer. `config.py` is the only place the numbers are written.

## What this fixed

Worth recording, because none of it was visible from the UI:

- **There was no server-side size limit at all.** The route passed `size = 0` into
  storage and saved `0` on the row, so nothing in the request path ever knew how big a
  file was. The only cap in the product was Uppy's, in the browser, and
  `POST /api/v1/storage/` accepts anonymous uploads — one `curl -F` with a 2 GB file
  filled the volume. On the S3 backend it is worse: `s3_storage.py` reads the whole
  payload into memory in one piece to compute its signature.
- **The browser cap was not applied either.** `restrictions` is an Uppy **Core** option.
  It was being passed through the Dashboard plugin's props, and `restrictions` appears
  nowhere in `@uppy/dashboard`'s types, so the picker had neither a size cap nor a type
  filter: it would accept an SVG. An earlier fix in that file (`props` rather than
  `properties`) was a real bug correctly identified and corrected in the wrong place.
- **The quota could not bite.** It was `used > limit`, so an account at zero bytes could
  upload a file of any size; and `used` is maintained by the `calculate_hash` arq job,
  so with the `worker` container down it stays at zero forever and the check never
  fires. It is now `used + this_file > limit`, and the row carries the real size at
  insert rather than waiting for the worker.
- **`POST /storage/raw` took any `Content-Type`,** SVG included, while the multipart
  route next to it enforced an allow-list — which made the allow-list advisory. It now
  uses the same table.
- **`video/mp4` was accepted with no UI in front of it**: `/edit/videos` is hidden and
  the editor passes `video_upload={false}`, so the only thing the allowance bought was
  an unbounded upload path. Behind `enable_video_upload`, off, with its own ceiling for
  whenever it is turned on.

Covered by `TestStorage` in `frogquiz/tests/test_server.py` (the boundary both ways, the
empty file, the published limits, the middleware, the unaccepted type on `/raw`, the
mid-stream abort, and that the row records its real size) and by
`frontend/src/lib/editor/upload_limits.test.ts`, which asserts the browser's fallbacks
are never looser than `config.py`.
