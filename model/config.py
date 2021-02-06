#!/usr/bin/python3

import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from model.models import *


class DatabaseQuery:
    __engine = None
    __session = None

    def __init__(self):
        self.__engine = sqlalchemy.create_engine(
            "postgresql://postgres:Admin1234*@localhost/hospital"
        )

    def add(self, obj):
        self.__session.add(obj)

    def add_services(self, services, hospital):
        all_services_by_hospital = []
        current_services = self.get_all_services()
        for s in current_services:
            if s.service in services:
                hospital.services.append(s)
                all_services_by_hospital.append(s.service)
        for s in services:
            if s in all_services_by_hospital:
                pass
            else:
                new_service = Service(service=s)
                self.__session.add(new_service)
                hospital.services.append(new_service)

    def check_id(self, user_id):
        if len(user_id) < 1 or not user_id:
            return False
        user = self.get_by_id(user_id)
        if type(user) != dict:
            return False
        return True

    def query(self, query):
        objects = {}
        queri = eval(query)
        for row in self.__session.query(queri).all():
            key = str(row.id)
            objects[key] = row
        return objects

    def get_all_services(self):
        return self.__session.query(Service).all()

    def get_by_id(self, id):
        objects = {}
        for element in ["Hospital", "Doctor", "Patient"]:
            objects = self.query(element)
            if id in objects:
                return objects[id]
        return objects

    def query_mail(self, query):
        objects = {}
        queri = eval(query)
        for row in self.__session.query(queri).all():
            key = str(row.email)
            objects[key] = row
        return objects

    def get_by_mail(self, mail):
        objects = {}
        for element in ["Hospital", "Doctor", "Patient"]:
            objects = self.query_mail(element)
            if mail in objects:
                return objects[mail]
        return objects

    def is_valid_user(self, usr_id):
        user = self.get_by_id(usr_id)
        if "Hospital" in str(user.__class__):
            return True
        return False

    def observation_by_patient_id(self, id):
        return (
            self.__session.query(Observation).filter(Observation.patient_id == id).all()
        )

    def get_doctor_by_id(self, user_id):
        return self.__session.query(Doctor).filter(Doctor.id == user_id).first()

    def get_patient_by_id(self, user_id):
        return self.__session.query(Patient).filter(Patient.id == user_id).first()

    def commit(self):
        self.__session.commit()

    def init_config(self):
        Base.metadata.create_all(self.__engine)
        sess_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Session = scoped_session(sess_factory)
        self.__session = Session

    def close(self):
        self.__session.remove()
