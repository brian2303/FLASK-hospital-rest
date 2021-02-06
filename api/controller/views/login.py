#!/usr/bin/python3

from api.controller.app import generate_usr_token, confirm_token
from flask_mail import Message

from api.controller.views import controller
from flask import jsonify, abort, request
from model import session_project
from model.models import *
from flask_jwt_extended import create_access_token
import datetime


@controller.route("/login", methods=["POST"])
def login():

    content = request.get_json()

    if content is None:
        abort(400, "You need to send data")

    id = content.get("id")
    password = content.get("password")

    user = session_project.get_by_id(id)
    if type(user) == dict:
        return (
            jsonify(
                {
                    "error": "you need sign up before contiuning",
                }
            ),
            401,
        )

    is_authorized = user.check_password(password)

    if not is_authorized:
        return {"error": "user or password incorrect"}, 401

    if not user.is_active:
        if user.__class__.__name__ == "Doctor":
            expires = datetime.timedelta(days=3)
            access_token = create_access_token(
                identity=str(user.id), expires_delta=expires
            )
            return (
                jsonify({"http://0.0.0.0:5000/api/change_password": access_token}),
                200,
            )
        return {"error": "You need to check your email first"}, 401

    expires = datetime.timedelta(days=3)
    access_token = create_access_token(identity=str(user.id), expires_delta=expires)

    return jsonify({str(user.__class__.__name__): access_token})
