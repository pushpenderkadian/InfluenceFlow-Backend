from app.config import settings
from helpers.queue_helper import create_queue
from micro_services.emailing_service.email_helper import send_outreach_message_to_creator
from app.database import get_db_session
import time
import asyncio
import logging

logger = logging.getLogger(__name__)

async def fetch_and_process_outreach(outreach_id):
    db_session = None
    try:
        # Get database session using the helper function
        db_session = await get_db_session()
        
        # Pass the database session to the function
        result = await send_outreach_message_to_creator(outreach_id, db_session)
        if result:
            print(f"Successfully processed outreach ID: {outreach_id}")
        else:
            print(f"Failed to process outreach ID: {outreach_id}")
    except Exception as e:
        logger.error(f"Error processing outreach ID {outreach_id}: {e}")
        print(f"Error processing outreach ID {outreach_id}: {e}")
    finally:
        if db_session:
            try:
                await db_session.close()
            except Exception as e:
                logger.error(f"Error closing database session: {e}")

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
            if payload:
                print(f"Email payload: {payload}")
                outreach_id = payload["outreach_id"]
                status = payload["status"]
                if status == "initiated":
                    print(f"Sending email outreach for {outreach_id} with status {status}")
                    asyncio.run(fetch_and_process_outreach(outreach_id))
            else:
                pass
                # print("No messages in the queue, waiting...")
        except Exception as e:
            print(f"Error consuming message: {e}")
        finally:
            time.sleep(1)

if __name__ == "__main__":
    consume()