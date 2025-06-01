from app.models import OutreachLog
from app.services.email_service import EmailService

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from datetime import timedelta
from typing import List


async def send_outreach_message_to_creator(outreach_id, db):
    query = text(f"""
        select * from outreach_log where id = {outreach_id}
    """)
    try:
        result = await db.execute(query)
        outreach = result.scalar_one_or_none()
        if not outreach:
            print(f"No outreach found for ID: {outreach_id}")
            return False

        email = outreach.recipient_contact
        EmailService.send_email(
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