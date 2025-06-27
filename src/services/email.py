from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
import os
from dotenv import load_dotenv
from src.services.email_token import create_email_token

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
    TEMPLATE_FOLDER="./src/templates"
)

async def send_verification_email(email: EmailStr, username, host):
    token = await create_email_token({"sub": email})
    message = MessageSchema(
        subject="Email Verification",
        recipients=[email],
        template_body = {"host": host, "username": username, "token": token},
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name = "templates.html")