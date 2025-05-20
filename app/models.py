from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_tutor = db.Column(db.Boolean, default=False)
    tutor_profile = db.relationship('TutorProfile', uselist=False, back_populates='user')
    reviews = db.relationship('Review', back_populates='student')

class TutorProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bio = db.Column(db.Text)
    subjects = db.Column(db.String(128))  # Comma-separated list
    availability = db.Column(db.String(128))  # e.g., 'Lunes 10-12, Martes 14-16'
    user = db.relationship('User', back_populates='tutor_profile')
    bookings = db.relationship('Booking', back_populates='tutor_profile')
    reviews = db.relationship('Review', back_populates='tutor')

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tutor_profile_id = db.Column(db.Integer, db.ForeignKey('tutor_profile.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subject = db.Column(db.String(64))
    datetime = db.Column(db.String(64))
    status = db.Column(db.String(32), default='pendiente')  # pendiente, confirmada, completada
    tutor_profile = db.relationship('TutorProfile', back_populates='bookings')
    student = db.relationship('User')

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor_profile.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    tutor = db.relationship('TutorProfile', back_populates='reviews')
    student = db.relationship('User', back_populates='reviews')
