from app.models import OutreachLog
from app.services.email_service import EmailService
from sqlalchemy import select, text
from datetime import timedelta
from typing import List
import requests
from app.config import settings


async def send_whatsapp_outreach_message_to_creator(outreach_id, db):
    query = text(f"""
        select * from outreach_logs where id = {outreach_id}
    """)
    try:
        result = await db.execute(query)
        outreach = result.scalar_one_or_none()
        if not outreach:
            print(f"No outreach found for ID: {outreach_id}")
            return False

        phone = outreach.recipient_contact

        try:
            whatsapp_agent_api_url = f"{settings.WHATSAPP_AGENT_API_URL}/send_message"
            payload = {
                "phone": phone,
                "message": outreach.message,
                "subject": outreach.subject
            }
            response = requests.post(url=whatsapp_agent_api_url, json=payload)
            response.raise_for_status()
            print("WhatsApp message sent successfully.")
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return False

    except Exception as e:
        print(f"Error fetching outreach data: {e}")
        return False
    return True

