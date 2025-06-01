from helpers.queue_helper import create_queue
from app.config import settings

queue = create_queue(
    queue_name=settings.EMAIL_QUEUE_NAME,
    host=settings.RABBITMQ_HOST,
    port=settings.RABBITMQ_PORT,
    user=settings.RABBITMQ_USER,
    password=settings.RABBITMQ_PASSWORD,
    vhost=settings.RABBITMQ_VHOST
)

message = {
    "outreach_id": 9,
    "status": "initiated",
}
queue.put(message)