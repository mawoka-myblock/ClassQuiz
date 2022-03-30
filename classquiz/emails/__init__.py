import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, PackageLoader, select_autoescape

from classquiz.config import settings
from classquiz.db.models import User

settings = settings()

jinja = Environment(
    loader=PackageLoader('classquiz.emails', 'templates'),
    autoescape=select_autoescape(['html', 'xml']),
    enable_async=True)


def _sendMail(template: str, to: str, subject: str):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = settings.mail_address
    msg['To'] = to
    msg.attach(MIMEText(template, 'html'))
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    server = smtplib.SMTP(host=settings.mail_server, port=settings.mail_port)
    server.ehlo()
    server.starttls(context=context)
    server.ehlo()
    server.login(settings.mail_username, settings.mail_password)
    server.sendmail(settings.mail_address, to, msg.as_string())


async def send_register_email(email: str):
    user = await User.objects.get_or_none(email=email, verified=False)
    if user is None:
        raise ValueError('User not found')
    template = jinja.get_template('register.jinja2')
    template = await template.render_async(
        base_url=settings.root_address,
        token=user.verify_key
    )
    _sendMail(template=template, to=email, subject='Verify your email')
