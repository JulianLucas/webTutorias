from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config

# --- Firebase Admin SDK ---
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db_firestore = firestore.client()

# Inicialización de extensiones
login_manager = LoginManager()
db = SQLAlchemy()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from .routes import auth, tutor, student, booking, review, main
    from . import models
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(tutor.bp)
    app.register_blueprint(student.bp)
    app.register_blueprint(booking.bp)
    app.register_blueprint(review.bp)

    return app
