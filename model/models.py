import model
import sqlalchemy as db
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    String,
    Integer,
    Boolean,
    Table,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from flask_bcrypt import generate_password_hash, check_password_hash
from uuid import uuid4, UUID


Base = declarative_base()


class User:

    id = Column(String(45), primary_key=True)
    email = Column(String(60), unique=True)
    phone_number = Column(String(45))
    password = Column(String(60))
    name = Column(String(60))
    address = Column(String(60))
    is_active = Column(Boolean, unique=False, default=False)

    def __init__(self, *args, **kwargs):
        if kwargs:
            for key, value in kwargs.items():
                if key != "__class__" and key != "activo":
                    setattr(self, key, value)

    def encrypt_password(self):
        self.password = generate_password_hash(self.password).decode("utf8")

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def create_user(self):
        model.session_project.add(self)
        model.session_project.commit()


class Hospital(User, Base):

    __tablename__ = "hospital"

    doctors = relationship("Doctor", backref="hospital_med")
    patients = relationship("Patient", backref="hospital_pati")
    services = relationship(
        "Service", secondary="hospital_service", backref="hospital", viewonly=False
    )

    def get_observations(self):
        doctors = self.doctors
        doc_observations = []
        for doctor in doctors:
            doc_observations.append(doctor.observations)

        return [obs.to_dict() for sub_list in doc_observations for obs in sub_list]


class Patient(User, Base):
    __tablename__ = "patients"
    date_of_birth = Column(String(60))
    hospital_id = Column(String(60), ForeignKey("hospital.id"), nullable="False")
    observations = relationship("Observation", backref="patient")

    def get_observations(self):
        observations = []
        for observation in self.observations:
            observations.append(observation.to_dict())
        return observations


class Service(Base):
    __tablename__ = "services"
    service = Column(String(60), primary_key=True, nullable=False)


hospital_service = Table(
    "hospital_service",
    Base.metadata,
    Column(
        "hospital_id",
        String(60),
        ForeignKey("hospital.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "service_id",
        String(60),
        ForeignKey("services.service", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Observation(Base):

    __tablename__ = "observations"

    id = Column(Integer, primary_key=True)
    observation = Column(Text, nullable=False)
    status_patient = Column(String(45), nullable=False)
    speciality = Column(String(50), nullable=False)
    doctor_id = Column(String(50), ForeignKey("doctors.id"), nullable=False)
    patient_id = Column(String(50), ForeignKey("patients.id"), nullable=False)

    def to_dict(self):
        dict_observation = {}
        dict_observation["info_patient"] = self.to_dict_info_patient()
        dict_observation["info_hospital"] = self.to_dict_info_hospital()
        return dict_observation

    def to_dict_info_patient(self):
        dict_patient = {}
        dict_patient["observation"] = self.observation
        dict_patient["status_patient"] = self.status_patient
        return dict_patient

    def to_dict_info_hospital(self):
        dict_info_hospital = {}
        doctor = model.session_project.get_by_id(self.doctor_id)
        hospital = model.session_project.get_by_id(doctor.hospital_id)
        dict_info_hospital["doctor"] = doctor.name
        dict_info_hospital["hospital"] = hospital.name
        dict_info_hospital["speciality"] = self.speciality

        return dict_info_hospital


class Doctor(User, Base):
    __tablename__ = "doctors"

    speciality = Column(String(60))
    hospital_id = Column(String(60), ForeignKey("hospital.id"), nullable="False")
    observations = relationship("Observation")

    def get_observations(self):
        observations = []
        for observation in self.observations:
            observations.append(observation.to_dict())
        return observations
