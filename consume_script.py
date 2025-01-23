import json
from app.services.event_bus import consume_event

EVENT_LOG_FILE = "event_log.json"

def handle_message(message):
    print("Received message:", message)

    try:
        with open(EVENT_LOG_FILE, "r", encoding="utf-8") as file:
            event_log = json.load(file)
    except FileNotFoundError:
        event_log = []

    event_log.append(message)

    with open(EVENT_LOG_FILE, "w", encoding="utf-8") as file:
        json.dump(event_log, file, indent=4)

if __name__ == "__main__":
    print("Waiting for messages from RabbitMQ...")
    consume_event("user_actions", handle_message)
