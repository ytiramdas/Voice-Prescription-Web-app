from inspect import signature
from flask import render_template, url_for, flash, redirect, current_app
from flask_login import login_user, current_user, logout_user, login_required
from voiceprescription import app, db, bcrypt
from voiceprescription.forms import PrescriptionForm, LoginForm, RegistrationForm, GetPrescriptionsForm
from datetime import date
from flask.globals import request
from voiceprescription.models import Doctors, Patients, User
from voiceprescription.utils import save_file_licenese, save_file_sign
from werkzeug.utils import secure_filename
import os, secrets

prescriptions = [
    {
        'doctor_name': 'Corey Schafer',
        'patient_name': 'Yasaswini Tiramdas',
        'date_of_diagnosis': '2021-03-11',
        'prescription': 'Dolo - thrice a day after a meal;',
        'diagnosis': 'High Fever',
        'symptoms': 'High Temperature, Sweating',
        'advice': 'Rest well',
        'signature': 'CoreySchafer..'
    },
    {
        'doctor_name': 'Subramanian',
        'patient_name': 'Yasaswini Tiramdas',
        'date_of_diagnosis': '2021-04-22',
        'prescription': 'Dolo - thrice a day after a meal;',
        'diagnosis': 'High Fever',
        'symptoms': 'High Temperature, Sweating',
        'advice': 'Rest well',
        'signature': 'Subramanian..'
    }
]

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check username and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # if current_user.is_authenticated:
    #     return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        type = ''
        if form.type.data=='Doctor':
            type = 'd'
        else:
            type = 'p'
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, type=type)
        db.session.add(user)
        db.session.commit()
        u = User.query.filter_by(username=form.username.data).first()
        if type == 'd':
            doc = Doctors(user_id=u.id, specialisation=form.specialisation.data, license_no=form.license_no.data, license_file = form.license_file.data.filename, signature_file = form.signature_file.data.filename)
            db.session.add(doc)
            db.session.commit()
        else:
            pat = Patients(user_id=u.id, is_diabetic=form.is_diabetic.data, hypertension=form.hypertension.data)
            db.session.add(pat)
            db.session.commit()
        flash(f'Account created. You can now login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    return "<h1>reset password<h1>"

@app.route('/homedoctor')
def homedoctor():
    return render_template('homedoctor.html', type="Doctor")

@app.route('/homepatient')
def homepatient():
    return render_template('homepatient.html', type="Patient")
 
@app.route('/prescription', methods=['GET', 'POST'])
def prescription():
    form = PrescriptionForm()
    if form.validate_on_submit():
        d = dict()
        d['doctor_name']= 'Corey Schafer'
        d['patient_name']=request.form['first_name'] + ' ' + request.form['last_name']
        today = date.today()
        d['date_of_diagnosis']= today.strftime("%B %d, %Y")
        d['age'] = request.form['age']
        d['gender'] = request.form['gender']
        d['prescription']= request.form['medicines']
        d['diagnosis'] = request.form['diagnosis']
        d['symptoms'] = request.form['symptoms']
        d['advice'] = request.form['advice']
        d['signature'] = request.form['first_name'] + '....'
        prescriptions.append(d)
        flash('Precription sent to Patient!', 'success')
        return redirect(url_for('homedoctor'))
    return render_template('prescription.html', title="Create Prescription", form=form)
 
@app.route('/getprescriptionforpatient', methods=['GET', 'POST'])
def getprescriptionforpatient():
    patient_info = [i for i in prescriptions if i['patient_name']=='Yasaswini Tiramdas']
    return render_template('getprescriptionsforpatient.html', prescriptions=patient_info)

@app.route('/getprescriptionfordoctor', methods=['GET', 'POST'])
def getprescriptionfordoctor():
    form = GetPrescriptionsForm()
    if form.validate_on_submit():
        flash('Got the precriptions!', 'success')
        p_name = form.name.data
        return redirect(url_for('getprescription', p_name = p_name))
    # return render_template('getprescriptions.html', title="Create Prescription", form=form, prescriptions=prescriptions)
    # patient_info = [i for i in prescriptions if i['patient_name']=='Yasaswini Tiramdas']
    return render_template('getprescriptionsfordoctor.html', form=form)

@app.route('/getprescription/<p_name>')
def getprescription(p_name):
    patient_info = [i for i in prescriptions if i['patient_name']==p_name]
    if len(patient_info)==0:
        flash('No users found')
        return redirect('getprescriptionfordoctor')
    return render_template('getprescription.html', prescriptions = patient_info)

@app.route('/doctorhistory')
def doctorhistory():
    patient_info = [i for i in prescriptions if i['doctor_name']=='Corey Schafer']
    return render_template('doctorhistory.html', prescriptions = patient_info)
