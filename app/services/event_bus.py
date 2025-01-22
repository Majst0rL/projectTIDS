#app/services/event_bus.py

import logging

logging.basicConfig(
    filename="event_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

def log_event(message):
    logging.info(message)
    print(f"Event logged: {message}")