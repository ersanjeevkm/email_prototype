from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from email_prototype.db_models import User
from flask_login import current_user


class Login(FlaskForm):
    email = StringField("Email-Id", validators=[DataRequired(), Email(), Length(min=5, max=50)])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")

class Signup(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=5, max=50)])
    email = StringField("Email-Id", validators=[DataRequired(), Email(), Length(min=5, max=50)])
    password = PasswordField("Password", validators=[DataRequired()])
    confirmpassword = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Signup")

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("This Username is already taken ! ")

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError("This Email is already taken ! ")

class Account(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=5, max=50)])
    email = StringField("Email-Id", validators=[DataRequired(), Email(), Length(min=5, max=50)])
    picture = FileField("Update your profile pic", validators=[FileAllowed(['jpeg','jpg','png'])])
    submit = SubmitField("Commit changes")

    def validate_username(self, username):
        if current_user.username != username.data:
           if User.query.filter_by(username=username.data).first():
                raise ValidationError("This Username is already taken ! ")

    def validate_email(self, email):
        if current_user.email != email.data:
           if User.query.filter_by(email=email.data).first():
                raise ValidationError("This Email is already taken ! ")

class Newmail(FlaskForm):
    receiver = StringField("Recipient", validators=[DataRequired(), Length(min=5, max=50)])
    subject = StringField("Subject", validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    draft = SubmitField('Save as draft')
    submit = SubmitField("Send mail")

    def validate_receiver(self, receiver):
        if User.query.filter_by(email=receiver.data).first():
            pass
        else:
            raise ValidationError(f"Email : {receiver.data} is not registered to this app ! ")

class Editdraft(FlaskForm):
    receiver = StringField("Recipient", validators=[DataRequired(), Length(min=5, max=50)])
    subject = StringField("Subject", validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Save changes')

    def validate_receiver(self, receiver):
        if User.query.filter_by(email=receiver.data).first():
            pass
        else:
            raise ValidationError(f"Email : {receiver.data} is not registered to this app ! ")

class Resetrequest(FlaskForm):
    email = StringField("Email-Id", validators=[DataRequired(), Email(), Length(min=5, max=50)])
    pass_email = StringField("Email-Id to send password reset link", validators=[DataRequired(), Email(), Length(min=5, max=50)])
    submit = SubmitField('Send reset link')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            pass
        else:
            raise ValidationError(f"Email : {email.data} is not registered to this app ! ")

class Passwordreset(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    confirmpassword = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset password')
