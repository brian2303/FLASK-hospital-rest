#!/usr/bin/python3
from api.controller.app import generate_usr_token, confirm_token, mail
from flask_mail import Message

from api.controller.views import controller
from flask import jsonify, abort, request
from model import session_project
from model.models import *


@controller.route("/add_user", methods=["POST"])
def add_user():
    content = request.get_json()
    user = content.get("user")
    user_id = content.get("data").get("id")

    if not session_project.check_id(user_id):
        return jsonify({"error": "id registrado en sistema"}), 401

    if user == "hospital":
        services = content.get("services")
        if len(services) < 1:
            return jsonify({"error": "services required"}), 401

        hospital = Hospital(**content["data"])
        hospital.encrypt_password()
        session_project.add(hospital)
        session_project.add_services(services, hospital)
        session_project.commit()
        endpoint_confirm = "http://0.0.0.0:5000/api/accept_add/"
        token = str(generate_usr_token(hospital.email))
        endpoint_confirm += token

    elif user == "paciente":
        patient = Patient(**content["data"])
        patient.encrypt_password()
        session_project.add(patient)
        session_project.commit()
        endpoint_confirm = "http://0.0.0.0:5000/api/accept_add/"
        token = str(generate_usr_token(patient.email))
        endpoint_confirm += token
    else:
        return jsonify({"error": "user isn't valid "}), 400

    msg = Message(recipients=[content.get("data").get("email")])
    msg_body = f'<a href="{endpoint_confirm}">Confirmar registro</a>'
    msg.subject = "Confirmar registro"
    msg.html = msg_body
    mail.send(msg)
    return jsonify({"status": "Resource created Sucessfully"}), 201


@controller.route("/accept_add/<token>")
def accept_add(token):
    try:
        email = confirm_token(token)
        user = session_project.get_by_mail(email)
        user.is_active = True
        user.create_user()
        return jsonify({"status": "Account verified successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Error during verification"}), 500
