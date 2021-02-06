#!/usr/bin/python3

from api.controller.app import generate_usr_token, confirm_token, app
from flask_mail import Message
from api.controller.views import controller
from flask import jsonify, abort, request, send_from_directory
from model import session_project
from model.models import *
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
import datetime
import os
import flask_excel as excel


@controller.route("/change_password", methods=["POST"])
@jwt_required
def change_password():

    content = request.get_json()

    if content is None:
        abort(400, "Content no should be empty")

    current_user = get_jwt_identity()
    print(current_user)

    old = content.get("old_password")
    new = content.get("new_password")

    user = session_project.get_by_id(current_user)

    is_authorized = user.check_password(old)
    if not is_authorized:
        return {"error": "Not allowed"}, 401

    user.password = new
    user.encrypt_password()
    if user.__class__.__name__ == "Doctor":
        user.is_active = True
    user.create_user()

    return jsonify({"status": "ok"}), 200


@controller.route("/reset_password", methods=["POST"])
def reset_password():
    content = request.get_json()

    if content is None:
        abort(400, "Not es un JSON")

    user = session_project.get_by_mail(content.get("email"))
    access_token = str(generate_usr_token(user.email))
    mail = "http://0.0.0.0:5000/api/reset/" + access_token
    return jsonify({"status": mail}), 200


@controller.route("/reset/<token>", methods=["GET", "POST"])
def reset(token):
    if request.method == "GET":
        try:
            email = confirm_token(token)
            return jsonify({"status": "Token verified successfully"}), 200
        except Exception as e:
            return jsonify({"status": "Invalid args"}), 401

    if request.method == "POST":
        try:
            email = confirm_token(token)
        except Exception as e:
            pass
        user = session_project.get_by_mail(email)
        content = request.get_json()
        if content is None:
            abort(400, "Invalid data")

        try:
            user.password = content.get("new_password")
            user.encrypt_password()
            user.create_user()
            return jsonify({"status": "Password updated"})
        except Exception as e:
            return jsonify({"error": "Invalid args"}), 401


@controller.route("/add_doctor", methods=["POST"])
@jwt_required
def add_doctor():

    data = request.get_json()
    user = get_jwt_identity()
    if not session_project.is_valid_user(user):
        return jsonify({"error": "user isn't allowed"}), 401

    doctor_id = data.get("data").get("id")
    if not session_project.check_id(doctor_id):
        return jsonify({"error": "user register in the sytem"}), 401

    d = Doctor(**data["data"])
    d.hospital_id = user
    d.encrypt_password()
    session_project.add(d)
    session_project.commit()
    return jsonify({"RESPONSE": "Doctor created successfully!"}), 201


@controller.route("/add_observation", methods=["POST"])
@jwt_required
def add_observation():

    data = request.get_json()
    status_patient = data.get("data").get("status_patient")
    doctor_id = get_jwt_identity()
    patient_id = data.get("data").get("patient_id")

    patient = session_project.get_patient_by_id(patient_id)
    user = session_project.get_doctor_by_id(doctor_id)
    if not patient:
        return jsonify({"error": "patient isn't add to the system"}), 400

    if user.__class__.__name__ != "Doctor":
        return jsonify({"error": "user unauthorized"}), 401

    if not status_patient or status_patient == "":
        return (
            jsonify({"error": "status_patient is required it isn't to be empty"}),
            400,
        )

    observation = Observation(**data["data"])
    session_project.add(observation)
    session_project.commit()

    return jsonify({"status": "ok"}), 200


@controller.route("/get_observations")
@jwt_required
def get_observations():

    user_id = get_jwt_identity()
    user = session_project.get_by_id(user_id)

    if user.__class__.__name__ == "Doctor":
        return jsonify({"observations": user.get_observations()}), 200

    elif user.__class__.__name__ == "Hospital":
        return jsonify({"observations": user.get_observations()}), 200

    elif user.__class__.__name__ == "Patient":
        return jsonify({"observation": user.get_observations()}), 200
    else:
        return jsonify({"error": "bad request"}), 400


@controller.route("/download_observations/<id>")
@jwt_required
def download_observations(id):

    observations = session_project.observation_by_patient_id(id)
    full_obs = []
    for o in observations:
        info_patient = o.to_dict().get("info_patient")
        info_hospital = o.to_dict().get("info_hospital")
        full_dict = {**info_patient, **info_hospital}
        full_obs.append(full_dict)

    return excel.make_response_from_records(full_obs, "csv")
