#!/usr/bin/python3

import os
from flask import Flask, make_response, jsonify
from model import session_project
from api.controller.views import controller
from flask import Blueprint
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail
from flask_bcrypt import Bcrypt
import flask_excel as excel

app = Flask(__name__)


cors = CORS(app, resources={r"/*": {"origins": "0.0.0.0"}})
app.config["SECRET_KEY"] = "t1NP63m4wnBg6nyHYKfmc2TpCOGI4nss"
app.config["SECURITY_PASSWORD_SALT"] = "security_app"
app.register_blueprint(controller)
jwt = JWTManager(app)
excel.init_excel(app)


bcrypt = Bcrypt(app)
app.config.update(
    dict(
        DEBUG=True,
        MAIL_SERVER="smtp.gmail.com",
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USE_SSL=False,
        MAIL_USERNAME=os.environ.get("SENDER_EMAIL"),
        MAIL_DEFAULT_SENDER=os.environ.get("SENDER_EMAIL"),
        MAIL_PASSWORD=os.getenv("SENDER_PASS"),
    )
)
mail = Mail(app)

def generate_usr_token(email):
    s = URLSafeTimedSerializer(
        app.config["SECRET_KEY"], salt=app.config["SECURITY_PASSWORD_SALT"]
    )
    return s.dumps(email, salt=app.config["SECURITY_PASSWORD_SALT"])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    try:
        email = serializer.loads(
            token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=expiration
        )
    except Exception as e:
        return False
    return email


@app.teardown_appcontext
def teardown_appcontext(self):
    session_project.close()


@app.errorhandler(404)
def not_found(error):
    """ Export json 404 error"""
    return make_response(jsonify({"error": "Not found"}), 404)


if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = os.getenv("API_PORT", 5000)
    app.run(host, port, threaded=True)
