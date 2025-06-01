from app.services.email_service import EmailService
import asyncio

email = "omkashyapcric@gmail.com"
subject = "Test Email"
body = "This is a test email."

asyncio.run(EmailService().send_email(
    to_email=email,
    subject=subject,
    body=body,
    is_html=False,
)
)
