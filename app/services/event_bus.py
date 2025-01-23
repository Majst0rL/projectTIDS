import pika
import json

import pika


def connect_to_rabbitmq():
    #localhost
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    return connection, channel


def consume_event(queue_name, callback):
    connection, channel = connect_to_rabbitmq()
    channel.queue_declare(queue=queue_name)

    def on_message(channel, method, properties, body):
        message = body.decode()
        callback(message)

    channel.basic_consume(queue=queue_name, on_message_callback=on_message, auto_ack=True)

    print(f"Waiting for messages from queue: {queue_name}. To exit, press CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Stopping consumer...")
        connection.close()


def publish_event(queue, message):
    connection, channel = connect_to_rabbitmq()
    channel.queue_declare(queue=queue)
    channel.basic_publish(exchange='', routing_key=queue, body=json.dumps(message))
    connection.close()
