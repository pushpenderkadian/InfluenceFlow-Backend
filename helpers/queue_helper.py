import json
import pika
import logging

logger = logging.getLogger(__name__)

class Queue:
    def __init__(self, queue_name, connection_url):
        self.queue_name = queue_name
        self.connection_url = connection_url
        self.connection = None
        self.channel = None
        self.setup_queue()

    def setup_queue(self):
        try:
            self.connection = pika.BlockingConnection(pika.URLParameters(self.connection_url))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name)
            print(f"Queue '{self.queue_name}' is set up.")
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Failed to connect to RabbitMQ: {e}")
        finally:
            if self.connection:
                self.connection.close()

    def put(self, message):
        print(message)
        try:
            connection = pika.BlockingConnection(pika.URLParameters(self.connection_url))
            print(connection)
            channel = connection.channel()
            channel.queue_declare(queue=self.queue_name)

            json_message = json.dumps(message)
            channel.basic_publish(exchange='', routing_key=self.queue_name, body=json_message)

            print(f"Sent message to queue '{self.queue_name}': {message}")
        except Exception as e:
            print(f"Failed to send message: {e}")
        finally:
            if connection:
                connection.close()

    def get(self):
        try:
            connection = pika.BlockingConnection(pika.URLParameters(self.connection_url))
            channel = connection.channel()
            channel.queue_declare(queue=self.queue_name)

            _, _, body = channel.basic_get(queue=self.queue_name, auto_ack=True)
            data = None
            if body:
                data = json.loads(body)
            return data
        except Exception as e:
            print(f"Error while consuming messages: {e}")
        finally:
            if connection:
                connection.close()


def create_queue(queue_name, host, port, user, password, vhost):
    scheme = "amqp"
    connection_url = f"{scheme}://{user}:{password}@{host}:{port}{vhost}?heartbeat=60"
    queue = Queue(queue_name, connection_url)
    return queue
