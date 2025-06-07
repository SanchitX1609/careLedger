from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from app.models import User, Role

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=80)
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(),
        Length(max=120)
    ])
    first_name = StringField('First Name', validators=[
        Optional(), 
        Length(max=50)
    ])
    last_name = StringField('Last Name', validators=[
        Optional(), 
        Length(max=50)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    role_id = SelectField('Role', coerce=int, validators=[DataRequired()])
    orphanage_id = SelectField('Orphanage', coerce=int, validators=[Optional()])
    submit = SubmitField('Register')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        from app.models import Role, Orphanage
        self.role_id.choices = [(r.id, r.name) for r in Role.query.all()]
        self.orphanage_id.choices = [(0, 'None')] + [(o.id, o.name) for o in Orphanage.query.all()]

    def validate_username(self, username):
        from wtforms.validators import ValidationError
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        from wtforms.validators import ValidationError
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    new_password2 = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')

class UserProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        Optional(), 
        Length(max=50)
    ])
    last_name = StringField('Last Name', validators=[
        Optional(), 
        Length(max=50)
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(),
        Length(max=120)
    ])
    submit = SubmitField('Update Profile')

    def __init__(self, original_email, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        from wtforms.validators import ValidationError
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already registered. Please choose a different one.')

class UserManagementForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=80)
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(),
        Length(max=120)
    ])
    first_name = StringField('First Name', validators=[
        Optional(), 
        Length(max=50)
    ])
    last_name = StringField('Last Name', validators=[
        Optional(), 
        Length(max=50)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    role_id = SelectField('Role', coerce=int, validators=[DataRequired()])
    orphanage_id = SelectField('Orphanage', coerce=int, validators=[Optional()])
    is_active = BooleanField('Active User', default=True)
    submit = SubmitField('Add User')

    def __init__(self, *args, **kwargs):
        super(UserManagementForm, self).__init__(*args, **kwargs)
        from app.models import Role, Orphanage
        self.role_id.choices = [(r.id, r.name) for r in Role.query.all()]
        self.orphanage_id.choices = [(0, 'None')] + [(o.id, o.name) for o in Orphanage.query.all()]

    def validate_username(self, username):
        from wtforms.validators import ValidationError
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        from wtforms.validators import ValidationError
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')
