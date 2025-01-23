from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import pika
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# RabbitMQ Connection Settings
RABBITMQ_HOST = "localhost"
QUEUE_NAME = "test_queue"

def send_message_to_queue(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=message)
    connection.close()

def consume_messages():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    def callback(ch, method, properties, body):
        print(f"Received message: {body.decode()}")
        # Emit the message to the client
        socketio.emit('new_message', {'message': body.decode()})

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
    print("Waiting for messages...")
    channel.start_consuming()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send():
    data = request.json
    message = data.get("message", "Default Message")
    send_message_to_queue(message)
    return jsonify({"status": "Message sent!"})

if __name__ == "__main__":
    # Start the consumer thread
    consumer_thread = threading.Thread(target=consume_messages)
    consumer_thread.daemon = True
    consumer_thread.start()

    # Start the Flask app
    socketio.run(app, debug=True)
