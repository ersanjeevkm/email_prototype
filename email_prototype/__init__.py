from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///email.db'
app.config["SECRET_KEY"] = 'f9e0997f75af4d3cc6fe87017a27ded5940ec519947f6d85a5174be902ada4b4'
app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = 'xxxxxxx'
app.config["MAIL_PASSWORD"] = 'xxxxxxx'

db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'
login.login_message_category = 'warning'
bcrypt = Bcrypt(app)
mail = Mail(app)

from email_prototype import routes
