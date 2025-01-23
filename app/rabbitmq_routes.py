from flask import Blueprint, render_template, request, jsonify
from .services.event_bus import publish_event

bp = Blueprint('rabbitmq', __name__)

@bp.route('/rabbitmq', methods=['GET', 'POST'])
def rabbitmq_demo():
    if request.method == 'POST':
        # Messaging
        event_message = {
            "event": "UserAction",
            "description": "User triggered an event via RabbitMQ."
        }
        publish_event("user_actions", event_message)
        return jsonify({"message": "Event published to RabbitMQ"}), 200

    return render_template('rabbitmq.html')
