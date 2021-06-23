from resurface import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    items = db.relationship('Item', backref='user', lazy='dynamic')
    reminders = db.relationship('Reminder', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    url = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    __table_args__ = (
        db.UniqueConstraint(url, user_id),
    )
    word_count = db.Column(db.Integer)
    time_added = db.Column(db.DateTime)
    source = db.Column(db.String)

    def __repr__(self):
        return '<Item {}>'.format(self.url)

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reminder_day = db.Column(db.String(120))
    reminder_time = db.Column(db.Time)
    reminder_items = db.Column(db.Integer)

    def __repr__(self):
        return '<Reminder {} items at {} on {}>'.format(
            self.reminder_items,
            self.reminder_time,
            self.reminder_day
        )
