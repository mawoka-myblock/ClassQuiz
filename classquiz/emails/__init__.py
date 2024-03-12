# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from jinja2 import Environment, PackageLoader, select_autoescape

from classquiz.config import settings, redis
from classquiz.db.models import User

settings = settings()

jinja = Environment(
    loader=PackageLoader("classquiz.emails", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
    enable_async=True,
)


def _sendMail(template: str, to: str, subject: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.mail_address
    msg["To"] = to
    msg["Date"] = formatdate(localtime=True)
    msg.attach(MIMEText(template, "html"))
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    server = smtplib.SMTP(host=settings.mail_server, port=settings.mail_port)
    server.ehlo()
    server.starttls(context=context)
    server.ehlo()
    server.login(settings.mail_username, settings.mail_password)
    server.sendmail(settings.mail_address, to, msg.as_string())


async def send_register_email(user: User):
    if user is None:
        raise ValueError("User not found")
    template = jinja.get_template("register.jinja2")
    template = await template.render_async(base_url=settings.root_address, token=user.verify_key)
    _sendMail(template=template, to=user.email, subject="Verify your email")


async def send_forgotten_password_email(email: str):
    user = await User.objects.get_or_none(email=email)
    if user is None:
        raise ValueError("User not found")
    template = jinja.get_template("forgotten_password.jinja2")
    token = os.urandom(32).hex()
    template = await template.render_async(base_url=settings.root_address, token=token)
    await redis.set(f"reset_passwd:{token}", str(user.id), ex=3600)
    _sendMail(template=template, to=email, subject="Reset your password")
    pass
