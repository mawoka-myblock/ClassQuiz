# SPDX-FileCopyrightText: 2026 frogQuiz contributors
#
# SPDX-License-Identifier: MPL-2.0

"""A throwaway SMTP server that writes every message it is handed to a file.

Why this exists: registration confirmation and password recovery are the two things
the app cannot paper over, and until now neither could be tested. `forgot-password`
answers 503 unless `mail_configured` is true, so with no relay in the e2e stack the
whole recovery path was unreachable -- the one journey MVP.md calls a must-do before
sharing.

Pointing the stack at this instead of a real relay tests the parts that actually
break: the Jinja templates render, the reset link is built from ROOT_ADDRESS and
points somewhere the app serves, and the token in it works exactly once. What it
does not test is whether a real provider accepts the mail, which is a deployment
question and stays on the manual checklist in DEPLOY.md.

Deliberately hand-rolled rather than aiosmtpd: the backend sends through plain
smtplib with no STARTTLS and no AUTH when the credentials are blank, so the subset
of SMTP needed here is EHLO/MAIL/RCPT/DATA/QUIT and nothing more. One fewer
dependency in the test path is worth sixty lines.
"""

import asyncio
import os
import sys
import time

OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "e2e/.data/mail"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 2526


async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    async def say(line: str) -> None:
        writer.write(f"{line}\r\n".encode())
        await writer.drain()

    await say("220 frogquiz-mailsink")
    try:
        while True:
            raw = await reader.readline()
            if not raw:
                return
            command = raw.decode("utf-8", "replace").strip()
            verb = command.split(" ", 1)[0].upper()

            if verb in ("EHLO", "HELO"):
                # No extensions advertised on purpose: no STARTTLS and no AUTH means
                # smtplib goes straight to MAIL FROM, which is what the app does when
                # MAIL_SECURITY=none and the credentials are blank.
                await say("250 frogquiz-mailsink")
            elif verb in ("MAIL", "RCPT"):
                await say("250 OK")
            elif verb == "DATA":
                await say("354 End data with <CR><LF>.<CR><LF>")
                lines: list[str] = []
                while True:
                    chunk = await reader.readline()
                    if not chunk:
                        return
                    text = chunk.decode("utf-8", "replace")
                    if text.rstrip("\r\n") == ".":
                        break
                    # Dot-stuffing, per RFC 5321: a body line that begins with a dot
                    # is sent with an extra one. Without this, a reset link that
                    # happened to wrap onto a line starting "." would come out wrong.
                    lines.append(text[1:] if text.startswith("..") else text)
                os.makedirs(OUT_DIR, exist_ok=True)
                # Monotonic-ish name so a test can take "the newest message" without
                # two messages in the same second colliding.
                name = f"{time.time():.6f}.eml".replace(".", "_", 1)
                tmp = os.path.join(OUT_DIR, f".{name}.part")
                with open(tmp, "w", encoding="utf-8") as fh:
                    fh.write("".join(lines))
                # Renamed into place, so a test never reads a half-written message.
                os.replace(tmp, os.path.join(OUT_DIR, name))
                await say("250 OK")
            elif verb == "QUIT":
                await say("221 Bye")
                return
            elif verb == "RSET":
                await say("250 OK")
            elif verb == "NOOP":
                await say("250 OK")
            else:
                await say("502 Command not implemented")
    except (ConnectionResetError, BrokenPipeError):
        return
    finally:
        writer.close()


async def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    server = await asyncio.start_server(handle, "127.0.0.1", PORT)
    print(f"mailsink listening on 127.0.0.1:{PORT}, writing to {OUT_DIR}", flush=True)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
