from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from ..models import User


class ManageUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    admin = RadioField('Admin', choices=['Admin', 'User'])
    submit = SubmitField('Update')

    def __init__(self, user):  # Passing the user attr from view to form
        super().__init__()
        self.user = user

    def validate_username(self, username):
        if username.data != self.user.username and User.query.filter_by(username=username.data).first():
            raise ValidationError('The username is already in use.')

    def validate_email(self, email):
        if email.data != self.user.email and User.query.filter_by(email=email.data.lower()).first():
            raise ValidationError('The email is already in use.')


class AddUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    admin = RadioField('Admin', choices=['Admin', 'User'], default='User')
    picture = FileField('Add Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Add User')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class AddAnnouncementForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=1, max=150)])
    submit = SubmitField('Post')
