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
        campaign_creator_id = outreach.campaign_creator_id

        query = text(f"""
            select * from campaign_creators where id = {campaign_creator_id}
        """)

        result = await db.execute(query)
        campaign_creator = result.scalar_one_or_none()
        if not campaign_creator:
            print(f"No campaign creator found for ID: {outreach_id}")
            return False
        
        campaign_id = campaign_creator.campaign_id
        creator_id = campaign_creator.creator_id

        query = text(f"""
            select * from campaigns where id = {campaign_id}
        """)
        result = await db.execute(query)
        campaign = result.scalar_one_or_none()
        if not campaign:
            print(f"No campaign found for ID: {campaign_id}")
            return False
        
        campaign_details = campaign.description
        campaign_name = campaign.title
        brand_name = campaign.brand_name

        query = text(f"""
            select * from creators where id = {creator_id}
        """)
        result = await db.execute(query)
        influencer = result.scalar_one_or_none()
        if not influencer:
            print(f"No influencer found for ID: {creator_id}")
            return False
        influencer_name = influencer.full_name

        try:
            whatsapp_agent_api_url = f"{settings.WHATSAPP_AGENT_API_URL}/send_message"
            headers={
                "Authorization": f"Bearer {settings.WHATSAPP_AGENT_API_TOKEN}",
            }
            payload = {
                "to": f"{phone}",
                "recipient_type": "individual",
                "type": "template",
                "template": {
                    "language": {
                        "policy": "deterministic",
                        "code": "en"
                    },
                    "name": "connect_influencer",
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": influencer_name
                                },
                                {
                                    "type": "text",
                                    "text": brand_name
                                },
                                {
                                    "type": "text",
                                    "text": campaign_details
                                },
                                {
                                    "type": "text",
                                    "text": campaign_details
                                }
                            ]
                        }
                    ]
                }
            }
            response = requests.post(url=whatsapp_agent_api_url,headers=headers, json=payload)
            response.raise_for_status()
            print("WhatsApp message sent successfully.")
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return False

    except Exception as e:
        print(f"Error fetching outreach data: {e}")
        return False
    return True

