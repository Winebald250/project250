from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Email, Length, InputRequired, ValidationError

def max_length_check(form, field):
    if len(field.data) > 5:
        raise ValidationError('You can select a maximum of 5 options.')

# Define the choices dictionary
subjects = [
    ('C++', 'C++'), 
    ('Python', 'Python'), 
    ('JavaScript', 'JavaScript'), 
    ('HTML', 'HTML'), 
    ('CSS', 'CSS')
]

days_of_week = [
    ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')
]

time_slots = [
    ('Morning', 'Morning'), ('Afternoon', 'Afternoon'), ('Evening', 'Evening')
]

languages = [
    ('English', 'English'), ('French', 'French'), ('Spanish', 'Spanish'), 
    ('Swahili', 'Swahili'), ('Kinyarwanda', 'Kinyarwanda')
]

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=50)])
    submit = SubmitField('Login')

class ProfileForm(FlaskForm):
    school = StringField('School/College Name', validators=[DataRequired(), Length(max=100)])
    primary_language = SelectField('Primary Language', choices=languages, validators=[DataRequired()])
    secondary_languages = SelectMultipleField('Secondary Languages', choices=languages, coerce=str)
    days = SelectMultipleField('Select your days availability', choices=days_of_week, validators=[InputRequired()])
    times = SelectMultipleField('Select your time availability', choices=time_slots, validators=[InputRequired()])
    strong_subjects = SelectMultipleField('Select your strong subjects', choices=subjects, validators=[InputRequired(), max_length_check])
    weak_subjects = SelectMultipleField('Select your weak subjects', choices=subjects, validators=[InputRequired(), max_length_check])
    submit = SubmitField('Complete Profile')

class VerifyEmailForm(FlaskForm):
    otp = StringField('Verify your email', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verify')

class ResendConfirmationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Resend Confirmation Email')

class CreateGroupForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired(), Length(max=100)])
    subject = SelectField('Select group subject', choices=subjects, validators=[InputRequired()])
    creator = StringField('Creator', validators=[DataRequired()])
    days = SelectMultipleField('Select your days availability', choices=days_of_week, validators=[InputRequired()])
    times = SelectMultipleField('Select your time availability', choices=time_slots, validators=[InputRequired()])
    submit = SubmitField('Create Group')
