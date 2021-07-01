from inspect import signature
from flask import render_template, url_for, flash, redirect, current_app, request
from flask_login import login_user, current_user, logout_user, login_required
from voiceprescription import app, db, bcrypt
from voiceprescription.forms import BookAppointment, PrescriptionForm, LoginForm, RegistrationForm, GetPrescriptionsForm
from datetime import date, datetime
from flask.globals import request
from voiceprescription.models import Appointments, Doctors, Patients, User, Prescriptions
from werkzeug.utils import secure_filename
import os, secrets
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_, and_
from sqlalchemy import create_engine
engine = create_engine('sqlite:///site.db')
Session = sessionmaker(bind = engine)
session = Session()

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
    if current_user.is_authenticated:
        if current_user.type == 'p':
            return redirect(url_for('homepatient'))
        elif current_user.type == 'd':
            return redirect(url_for('homedoctor'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if user.type == 'p':
                return redirect(next_page) if next_page else redirect(url_for('homepatient'))
            elif user.type == 'd':
                return redirect(next_page) if next_page else redirect(url_for('homedoctor'))
        else:
            flash('Login Unsuccessful. Please check username and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
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
            doc = Doctors(user_id=u.id, specialisation=form.specialisation.data, license_no=form.license_no.data)
            print(doc)
            f1 = request.files['license_file']
            random_hex = secrets.token_hex(8)
            _, f_ext = os.path.splitext(secure_filename(f1.filename))
            license_fn = random_hex + f_ext
            license_path = os.path.join(current_app.root_path, 'static/licenses', license_fn)
            f1.save(license_path)
            doc.license_file = license_fn
            f2 = request.files['signature_file']
            random_hex = secrets.token_hex(8)
            _, f_ext = os.path.splitext(secure_filename(f2.filename))
            signs_fn = random_hex + f_ext
            signs_path = os.path.join(current_app.root_path, 'static/signs', signs_fn)
            f1.save(signs_path)
            doc.signature_file = signs_fn
            print(doc)
            print(secure_filename(f1.filename))
            db.session.add(doc)
            db.session.commit()
        else:
            pat = Patients(user_id=u.id, is_diabetic=form.is_diabetic.data, hypertension=form.hypertension.data)
            print(pat)
            db.session.add(pat)
            db.session.commit()
        flash(f'Account created. You can now login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

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
        p = Prescriptions()
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

@app.route('/bookappointment', methods=['GET', 'POST'])
def bookappointment():
    form = BookAppointment()
    if form.validate_on_submit():
        appointment = Appointments(patient_id=current_user.id, time_of_appointment=form.date_of_appointment.data, specialisation=form.specialisation.data)
        print(appointment)
        all_doc = Doctors.query.filter_by(specialisation=form.specialisation.data).all()
        if all_doc:
            for doc in all_doc:
                app = Appointments.query.filter_by(doctor_id=doc.user_id).all()
                print(app)
                if app==[]:
                    print(doc.user_id)
                    appointment.doctor_id = doc.user_id
                    break
        else:
            flash('Appointment couldn\'t be booked as there are no doctors registered with that specialisation', 'danger')
            return redirect(url_for('homepatient'))
        
        if not appointment.doctor_id:
            flag = 0
            for doc in all_doc:
                app = Appointments.query.filter_by(doctor_id=doc.user_id).all()
                if abs((app.time_of_appointment - form.date_of_appointment.data).total_seconds() / 60.0) > 30:
                    appointment.doctor_id = doc.user_id
                    flag = 1
                    break;
            if flag == 0:
                flash('Appointment couldn\'t be booked as there are no doctors free at that time, Book at other time', 'danger')
                return redirect(url_for('homepatient'))
        print(all_doc)
        print(appointment)
        print(form.specialisation.data)
        print(form.date_of_appointment.data)
        db.session.add(appointment)
        db.session.commit()
        flash('Appointment is Booked successfully, Check your appointments for confirmation', 'success')
        return redirect(url_for('homepatient'))
    return render_template('bookappointment.html', form=form)

@app.route('/appointments')
def appointments():
    appointments = []
    if current_user.type == 'p':
        appointments = Appointments.query.join(User, (User.id == Appointments.doctor_id)).add_columns(User.username, User.email).filter(Appointments.patient_id == current_user.id).order_by(Appointments.time_of_appointment.desc()).all()
    else:
        appointments = Appointments.query.join(User, (User.id == Appointments.patient_id)).add_columns(User.username, User.email).filter(Appointments.doctor_id == current_user.id).order_by(Appointments.time_of_appointment.desc()).all()
    print(appointments)
    for i in appointments:
        print(i[0].id)
    return render_template('appointments.html', appointments = appointments)

@app.route('/appointments/<int:appoint_id>')
def accept_appointment(appoint_id):
    print(appoint_id)
    appointment = Appointments.query.filter_by(id = appoint_id).first()
    appointment.doctor_confirmation = 1
    appointment.time_of_appointment_cnf = datetime.utcnow()
    db.session.commit()
    return redirect(url_for('appointments'))

@app.route('/appointments/<int:appoint_id>')
def deny_appointment(appoint_id):
    Appointments.query.filter_by(id=appoint_id).delete()
    flash('Appointment is deleted', 'success')
    return redirect(url_for('appointments'))
