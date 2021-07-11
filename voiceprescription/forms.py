from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, validators, SelectField, TextAreaField, DateField, RadioField
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields.core import DateTimeField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from voiceprescription.models import Doctors, User
from datetime import datetime


specialization_chocies = [('Allergists/Immunologists', 'Allergists/Immunologists'), 
('Anesthesiologists', 'Anesthesiologists'),
('Cardiologists', 'Cardiologists'),
('ColonandRectalSurgeons', 'Colon and Rectal Surgeons'),
('Dermatologists', 'Dermatologists'),
('Endocrinologists', 'Endocrinologists'),
('FamilyPhysicians', 'Family Physicians'),
('GeneralPhysicians', 'General Physicians'),
('Gastroenterologists', 'Gastroenterologists'),
('Hematologists', 'Hematologists'),
('InfectiousDiseaseSpecialists', 'Infectious Disease Specialists'),
('Internists', 'Internists'),
('Nephrologists', 'Nephrologists'),
('Neurologists', 'Neurologists'),
('ObstetriciansandGynecologists', 'Obstetricians and Gynecologists'),
('Oncologists', 'Oncologists'),
('Ophthalmologists', 'Ophthalmologists'),
('Otolaryngologists', 'Otolaryngologists'),
('Physiatrists', 'Physiatrists'),
('Psychiatrists','Psychiatrists'),
('Urologists', 'Urologists')]

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    type = RadioField('Type of User', choices = ['Patient', 'Doctor'], validators=[DataRequired()])
    
    specialisation = SelectField('Specialisation', choices = specialization_chocies, validators=[DataRequired()])
    license_no = StringField('License Number', validators=[DataRequired(), Length(min=8, max=8)])
    license_file = FileField('License File', validators=[FileAllowed(['pdf'])])
    signature_file = FileField('Signature File', validators=[FileAllowed(['jpg', 'png', 'PNG'])])

    is_diabetic = RadioField('Is Diabatic', choices = ['Yes', 'No'], validators=[DataRequired()])
    hypertension = RadioField('Level of Hypertention', choices = ['Low', 'Normal', 'High'], validators=[DataRequired()])

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose another.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already taken. Please choose another.')

    def validate_license_no(self, license_no):
        user = Doctors.query.filter_by(license_no=license_no.data).first()
        if user:
            raise ValidationError('An account has already been created with this licence number')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')



class PrescriptionForm(FlaskForm):
    first_name = StringField('First Name',
                             validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name',
                            validators=[DataRequired(), Length(min=2, max=20)])
    age = IntegerField('Age',
                       validators=[DataRequired(), validators.NumberRange(min=1, max=100)])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
                         validators=[DataRequired()])
    medicines = TextAreaField('Medicines',
                              validators=[DataRequired(), Length(min=10, max=500)])
    symptoms = TextAreaField('Symptoms',
                             validators=[DataRequired(), Length(min=10, max=500)])
    diagnosis = StringField('Diagnosis',
                            validators=[DataRequired(), Length(min=5, max=80)])
    advice = StringField('Advice',
                         validators=[DataRequired(), Length(min=5, max=100)])
    submit = SubmitField('Create Prescription')


class GetPrescriptionsForm(FlaskForm):
    name = StringField('Name',
                             validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Get Prescriptions')

class BookAppointment(FlaskForm):
    date_of_appointment = DateTimeLocalField('Appointment Date and Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    specialisation = SelectField('Specialisation for Consultation', choices = specialization_chocies, validators=[DataRequired()])
    submit = SubmitField('Book Appointment')

    def validate_date_of_appointment(self, date_of_appointment):
        if date_of_appointment.data<datetime.now():
            raise ValidationError('Date and Time should be after current time stamp')
