import os

from flask import Flask
from .routes import bp as routes_bp
from .rabbitmq_routes import bp as rabbitmq_bp

def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.getcwd(), "templates"))
    app.register_blueprint(routes_bp)  # General routes
    app.register_blueprint(rabbitmq_bp, url_prefix="/rabbitmq")  # RabbitMQ routes
    return app
