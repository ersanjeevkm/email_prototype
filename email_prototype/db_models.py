from email_prototype import app
from datetime import datetime
from email_prototype import db, login
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as serializer

@login.user_loader
def loader(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    picture = db.Column(db.String(20), nullable=False, default='demo.jpg')
    inbox = db.relationship('Inbox', backref='Inboxuser', lazy=True)
    outbox = db.relationship('Outbox', backref='Outboxuser', lazy=True)
    draft = db.relationship('Draft', backref='Draftuser', lazy=True)

    def reset_request(self, duration=1800):
        s = serializer(app.config['SECRET_KEY'], duration)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token):
        s = serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return user_id

    def __repr__(self):
        return f'User : {self.id}, {self.username}'


class Inbox(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(50), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'Inbox Msg Id : {self.id}, Sub : {self.subject}'


class Outbox(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    receiver = db.Column(db.String(50), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'Outbox Msg Id : {self.id}, Sub : {self.subject}'


class Draft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    receiver = db.Column(db.String(50), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'Outbox Msg Id : {self.id}, Sub : {self.subject}'
