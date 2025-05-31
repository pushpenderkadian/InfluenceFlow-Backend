import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from typing import Dict, Any, Optional
import logging
from ..config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = False,
        from_name: str = "InfluenceFlow"
    ) -> bool:
        """Send email using SMTP"""
        try:
            if not self.smtp_username or not self.smtp_password:
                logger.warning("SMTP credentials not configured, using mock mode")
                logger.info(f"Mock email sent to {to_email}: {subject}")
                return True
            
            # Create message
            message = MIMEMultipart()
            message["From"] = f"{from_name} <{self.smtp_username}>"
            message["To"] = to_email
            message["Subject"] = subject
            
            # Add body
            if is_html:
                message.attach(MIMEText(body, "html"))
            else:
                message.attach(MIMEText(body, "plain"))
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=True,
                username=self.smtp_username,
                password=self.smtp_password,
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    async def send_campaign_invitation(
        self,
        creator_email: str,
        creator_name: str,
        campaign_title: str,
        brand_name: str,
        offered_rate: float,
        campaign_details: Dict[str, Any]
    ) -> bool:
        """Send campaign invitation email to creator"""
        
        template = Template("""
        Hi {{ creator_name }},

        We hope this email finds you well! We're reaching out from {{ brand_name }} with an exciting collaboration opportunity.

        Campaign: {{ campaign_title }}
        Offered Rate: ${{ offered_rate }}

        Campaign Details:
        {{ campaign_description }}

        We believe your content style and audience would be a perfect fit for this campaign. 

        If you're interested, please reply to this email or log into your InfluenceFlow dashboard to accept the invitation.

        Looking forward to working with you!

        Best regards,
        The {{ brand_name }} Team
        """)
        
        body = template.render(
            creator_name=creator_name,
            brand_name=brand_name,
            campaign_title=campaign_title,
            offered_rate=offered_rate,
            campaign_description=campaign_details.get('description', 'Please check your dashboard for full details.')
        )
        
        subject = f"Collaboration Opportunity: {campaign_title} - {brand_name}"
        
        return await self.send_email(creator_email, subject, body)
    
    async def send_contract_notification(
        self,
        creator_email: str,
        creator_name: str,
        campaign_title: str,
        contract_url: str
    ) -> bool:
        """Send contract signing notification"""
        
        template = Template("""
        Hi {{ creator_name }},

        Great news! Your contract for the {{ campaign_title }} campaign is ready for signing.

        Please review and sign your contract here: {{ contract_url }}

        Once signed, we can proceed with the campaign kickoff.

        Best regards,
        InfluenceFlow Team
        """)
        
        body = template.render(
            creator_name=creator_name,
            campaign_title=campaign_title,
            contract_url=contract_url
        )
        
        subject = f"Contract Ready for Signing - {campaign_title}"
        
        return await self.send_email(creator_email, subject, body)
    
    async def send_payment_notification(
        self,
        creator_email: str,
        creator_name: str,
        payment_amount: float,
        payment_type: str,
        campaign_title: str
    ) -> bool:
        """Send payment notification"""
        
        template = Template("""
        Hi {{ creator_name }},

        Good news! Your {{ payment_type }} payment of ${{ payment_amount }} for the {{ campaign_title }} campaign has been processed.

        You should see the payment in your account within 1-3 business days.

        Thank you for your amazing work on this campaign!

        Best regards,
        InfluenceFlow Team
        """)
        
        body = template.render(
            creator_name=creator_name,
            payment_amount=payment_amount,
            payment_type=payment_type,
            campaign_title=campaign_title
        )
        
        subject = f"Payment Processed - ${payment_amount} for {campaign_title}"
        
        return await self.send_email(creator_email, subject, body)

# Global instance
email_service = EmailService()