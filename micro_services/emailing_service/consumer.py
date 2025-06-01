from app.config import settings
from helpers.queue_helper import create_queue
from micro_services.emailing_service.email_helper import send_outreach_message_to_creator
from app.database import AsyncSession
import time
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings

DATABASE_URL = settings.DATABASE_URL  # Ensure this is correctly set in your config

# Create the database engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create the session factory
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def fetch_and_process_outreach(outreach_id):
    async with AsyncSession() as db:  # Create a new database session
        try:
            # Pass the database session explicitly to the function
            result = await send_outreach_message_to_creator(outreach_id, db)
            if result:
                print(f"Successfully processed outreach ID: {outreach_id}")
            else:
                print(f"Failed to process outreach ID: {outreach_id}")
        except Exception as e:
            print(f"Error processing outreach ID {outreach_id}: {e}")

def consume():
    queue = create_queue(
        queue_name=settings.EMAIL_QUEUE_NAME,
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        user=settings.RABBITMQ_USER,
        password=settings.RABBITMQ_PASSWORD,
        vhost=settings.RABBITMQ_VHOST
    )
    while True:
        try:
            payload = queue.get()
            print(f"Email payload: {payload}")
            if payload:
                outreach_id = payload["outreach_id"]
                status = payload["status"]
                if status == "initiated":
                    print(f"Sending email outreach for {outreach_id} with status {status}")
                    asyncio.run(fetch_and_process_outreach(outreach_id))
            else:
                print("No messages in the queue, waiting...")
        except Exception as e:
            print(f"Error consuming message: {e}")
        finally:
            time.sleep(1)

if __name__ == "__main__":
    consume()