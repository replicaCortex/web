from email.message import EmailMessage

import aiosmtplib

from app.config import (
    SMTP_FROM,
    SMTP_HOST,
    SMTP_PASS,
    SMTP_PORT,
    SMTP_SECURE,
    SMTP_USER,
)


class MailService:
    async def send_welcome_email(self, to_email: str, username: str):
        message = EmailMessage()
        message["From"] = SMTP_FROM
        message["To"] = to_email
        message["Subject"] = "Добро пожаловать в наше приложение!"

        message.set_content(
            f"Привет, {username}!\nСпасибо за регистрацию. Перейдите по ссылке для входа: http://localhost:3000/login"
        )

        message.add_alternative(
            f"""
            <html>
                <body>
                    <h2>Привет, {username}! 👋</h2>
                    <p>Спасибо за регистрацию в нашем приложении.</p>
                </body>
            </html>
            """,
            subtype="html",
        )

        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASS,
            use_tls=SMTP_SECURE,
        )


mail_service = MailService()
