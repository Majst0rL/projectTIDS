from flask import Flask
import os

def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.getcwd(), "templates"))
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)
    return app
