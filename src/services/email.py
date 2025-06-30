from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
import os
from dotenv import load_dotenv
from src.services.email_token import create_email_token
from src.auth.auth import create_password_reset_token

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
    TEMPLATE_FOLDER=os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../templates")
    ),
)


async def send_reset_email(email: str, username: str, host):
    token = await create_password_reset_token(email)
    message = MessageSchema(
        subject="Password Reset",
        recipients=[email],
        template_body={"host": host, "username": username, "token": token},
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    await fm.send_message(message, template_name="reset_password.html")


async def send_verification_email(email: EmailStr, username, host):
    """
    Отправляет письмо для подтверждения email с токеном в HTML-шаблоне.

    Args:
        email (EmailStr): Email адрес получателя.
        username (str): Имя пользователя для персонализации письма.
        host (str): URL хоста, используется в письме (например, для ссылки подтверждения).

    Returns:
        None
    """
    token = await create_email_token({"sub": email})
    message = MessageSchema(
        subject="Email Verification",
        recipients=[email],
        template_body={"host": host, "username": username, "token": token},
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name="templates.html")
