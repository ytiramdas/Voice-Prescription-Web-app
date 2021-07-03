from enum import unique
from re import T
from voiceprescription import db, login_manager
from datetime import datetime
from sqlalchemy.orm import relationship
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    type = db.Column(db.String(2), nullable=False, default='p')
    password = db.Column(db.String(60), nullable=False)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}', '{self.type}')"

class Doctors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    specialisation = db.Column(db.String(30), nullable=False)
    license_no = db.Column(db.String(20), nullable=False, unique=True)
    license_file = db.Column(db.String(20), nullable=False)
    signature_file = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"Doctor('{self.id}', '{self.user_id}', '{self.specialisation}, '{self.license_no}', '{self.license_file}', '{self.signature_file}')"

class Patients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_diabetic = db.Column(db.String(5), nullable=False, default='No')
    hypertension = db.Column(db.String(10), nullable=False, default='Normal')

    def __repr__(self):
        return f"Patient('{self.id}', '{self.user_id}', '{self.is_diabetic}', '{self.hypertension}')"

class Appointments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    specialisation = db.Column(db.String(30), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    doctor_confirmation = db.Column(db.Integer, nullable=False, default='0')
    doctor_change = db.Column(db.Integer, nullable=False, default='0')
    time_of_appointment = db.Column(db.DateTime, nullable=False)
    time_of_appointment_cnf = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    doctor = relationship("User", foreign_keys=[doctor_id])
    patient = relationship("User", foreign_keys=[patient_id])

    def __repr__(self):
        return f"Appointment('{self.id}', '{self.specialisation}', '{self.time_of_appointment}', '{self.time_of_appointment_cnf}', '{self.doctor_id}', '{self.patient_id}')"

class Prescriptions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    patient_name = db.Column(db.String(30), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    date_and_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    prescription = db.Column(db.String(150), nullable=False)
    diagnosis = db.Column(db.String(150), nullable=False)
    symptoms = db.Column(db.String(150), nullable=False)
    advice = db.Column(db.String(150), nullable=False)
    sign = db.Column(db.String(30), nullable=False)
    doctor = relationship("User", foreign_keys=[doctor_id])
    patient = relationship("User", foreign_keys=[patient_id])
    appointments = relationship("Appointments", foreign_keys=[appointment_id])
    def __repr__(self):
        return f"Prescription('{self.id}', '{self.patient_id}', '{self.doctor_id}', '{self.prescription}','{self.diagnosis}', '{self.advice}', '{self.symptoms}')"