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
    appointments = Appointments.query.filter(and_(Appointments.patient_id == current_user.id, Appointments.doctor_change==-1, Appointments.doctor_confirmation==0)).order_by(Appointments.time_of_appointment.desc()).all()
    if appointments:
        for a in appointments:
            flash("The appointment "+ str(a.id) +" was cancelled as there were no doctors available at that time", 'danger')
            a.doctor_confirmation = 1
        db.session.commit()
    appointments = Appointments.query.filter(and_(Appointments.patient_id == current_user.id, Appointments.doctor_change==1, Appointments.doctor_confirmation==0)).order_by(Appointments.time_of_appointment.desc()).all()
    if appointments:
        for a in appointments:
            flash("For appointment "+ str(a.id) +", new doctor was assigned", 'success')
            a.doctor_change = 0
        db.session.commit()
    return render_template('homepatient.html', type="Patient")

@app.route('/account')
def account():
    return render_template('account.html', title='Account')

@app.route('/prescription/<int:appoint_id>', methods=['GET', 'POST'])
def create_prescription(appoint_id):
    print(appoint_id)
    form = PrescriptionForm()
    if form.validate_on_submit():
        a = Appointments.query.filter_by(id=appoint_id).first()
        p = Prescriptions(patient_id=a.patient_id, doctor_id=a.doctor_id, age=form.age.data, appointment_id=appoint_id)
        p.patient_name = form.first_name.data + ' ' + form.last_name.data
        p.prescription = form.medicines.data
        p.diagnosis = form.diagnosis.data
        p.symptoms = form.symptoms.data
        p.advice = form.advice.data
        doc = Doctors.query.filter_by(user_id = a.doctor_id).first()
        p.sign = doc.signature_file
        db.session.add(p)
        db.session.commit()
        flash('Precription sent to Patient!', 'success')
        return redirect(url_for('homedoctor'))
    return render_template('prescription.html', title="Create Prescription", form=form, appoint_id=appoint_id)

@app.route('/history')
def history():
    if current_user.type=='p':
        patient_pres = Prescriptions.query.filter_by(patient_id=current_user.id).order_by(Prescriptions.date_and_time.desc()).all()
        return render_template('displayprescriptions.html', prescriptions=patient_pres)
    else:
        doctor_pres = Prescriptions.query.filter_by(doctor_id=current_user.id).order_by(Prescriptions.date_and_time.desc()).all()
        return render_template('displayprescriptions.html', prescriptions=doctor_pres)


@app.route('/getprescriptionfordoctor/<int:appoint_id>', methods=['GET', 'POST'])
def getprescriptionfordoctor(appoint_id):
    print(appoint_id)
    app = Appointments.query.filter_by(id = appoint_id).first()
    doctor_pres = Prescriptions.query.filter_by(patient_id=app.patient_id).order_by(Prescriptions.date_and_time.desc()).all()
    if doctor_pres == []:
        flash("No previous records of the user", 'success')
        return redirect(url_for('create_prescription', appoint_id=appoint_id))
    return render_template('getprescriptionsfordoctor.html', prescriptions=doctor_pres, appoint_id=appoint_id)


@app.route('/bookappointment', methods=['GET', 'POST'])
def bookappointment():
    form = BookAppointment()
    if form.validate_on_submit():
        appointment = Appointments(patient_id=current_user.id, time_of_appointment=form.date_of_appointment.data, specialisation=form.specialisation.data)
        print(appointment)
        all_doc = Doctors.query.filter_by(specialisation=form.specialisation.data).all()
        if all_doc:
            for doc in all_doc:
                app = Appointments.query.filter(and_(Appointments.doctor_id==doc.user_id, Appointments.doctor_change!=-1)).all()
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
                appoints = Appointments.query.filter(and_(Appointments.doctor_id==doc.user_id, Appointments.doctor_change!=-1)).all()
                for app in appoints:
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
        appointments = Appointments.query.filter(and_(Appointments.patient_id == current_user.id, Appointments.doctor_change!=-1)).order_by(Appointments.time_of_appointment.desc()).all()
    else:
        appointments = Appointments.query.filter(and_(Appointments.doctor_id == current_user.id, Appointments.doctor_change!=-1)).order_by(Appointments.time_of_appointment.desc()).all()
    app = []
    for i in appointments:
        p = Prescriptions.query.filter_by(appointment_id=i.id).first()
        if p == None:
            app.append(i)
    return render_template('appointments.html', appointments = app)

@app.route('/appointments/<int:appoint_id>/accept')
def accept_appointment(appoint_id):
    print(appoint_id)
    appointment = Appointments.query.filter_by(id = appoint_id).first()
    appointment.doctor_confirmation = 1
    appointment.time_of_appointment_cnf = datetime.utcnow()
    db.session.commit()
    return redirect(url_for('appointments'))

@app.route('/appointments/<int:appoint_id>/deny')
def deny_appointment(appoint_id):
    print(appoint_id)
    a = Appointments.query.filter_by(id=appoint_id).first()
    old_doc_id = a.doctor_id
    all_doc =  Doctors.query.filter(and_(Doctors.specialisation==a.specialisation, Doctors.user_id!=old_doc_id)).all()
    flag = 0
    if all_doc:
        for doc in all_doc:
            app = Appointments.query.filter(and_(Appointments.doctor_id==doc.user_id, Appointments.doctor_change!=-1)).all()
            print(app)
            if app==[]:
                print(doc.user_id)
                a.doctor_id = doc.user_id
                a.doctor_change = 1
                flag=1
                break
        if flag==0:
            flag = 0
            for doc in all_doc:
                appoints = Appointments.query.filter(and_(Appointments.doctor_id==doc.user_id, Appointments.doctor_change!=-1)).all()
                for app in appoints:
                    if abs((app.time_of_appointment - a.time_of_appointment).total_seconds() / 60.0) > 30:
                        print(doc.user_id)
                        a.doctor_id = doc.user_id
                        a.doctor_change = 1
                        flag = 1
                        break;
            if flag == 0:
                a.doctor_change = -1
    if flag==0:
        a.doctor_change = -1
    db.session.commit()
    flash('Appointment is deleted', 'success')
    return redirect(url_for('appointments'))

@app.route('/cancelled_appointments')
def cancelled_appointments():
    appointments = []
    if current_user.type=='p':
        appointments = Appointments.query.filter(and_(Appointments.patient_id==current_user.id, Appointments.doctor_change==-1)).order_by(Appointments.time_of_appointment.desc()).all()
    else:
        appointments = Appointments.query.filter(and_(Appointments.doctor_id==current_user.id, Appointments.doctor_change==-1)).order_by(Appointments.time_of_appointment.desc()).all()
    return render_template('cancelled_appointments.html', appointments = appointments)