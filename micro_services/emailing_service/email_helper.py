from app.services.email_service import EmailService
from app.models.outreach_log import OutreachLog, OutreachType

from sqlalchemy import  text


async def send_outreach_message_to_creator(outreach_id, db):
    query = text(f"""
        select * from outreach_logs where id = {outreach_id} and outreach_type = 'EMAIL'
    """)
    try:
        result = await db.execute(query)
        outreach = result.mappings().fetchone()
        
        outreach = OutreachLog(**outreach) if outreach else None
        if not outreach:
            print(f"No outreach found for ID: {outreach_id}")
            return False
        
        if outreach.outreach_type != 'EMAIL':
            print("Outreach type is not email, skipping.")
            return False

        email = outreach.recipient_contact
        await EmailService().send_email(
            to_email=email,
            subject=outreach.subject,
            body=outreach.message,
            is_html=False,
        )
        print("Mail sent successfully.")
        return True
    except Exception as e:
        print(f"Error fetching outreach data: {e}")
        return False