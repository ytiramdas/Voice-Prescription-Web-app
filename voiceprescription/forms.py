from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, validators, SelectField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose another.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already taken. Please choose another.')


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
    prescription_number = IntegerField('Prescription Number',
                                       validators=[DataRequired(), validators.NumberRange(min=1000, max=9999)])
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
