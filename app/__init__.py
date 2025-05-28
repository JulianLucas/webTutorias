from flask import Flask

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

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # SQLAlchemy eliminado. Toda la persistencia es en Firestore.
    @login_manager.user_loader
    def load_user(user_id):
        from app import db_firestore
        from flask_login import UserMixin
        users_ref = db_firestore.collection('users')
        doc = users_ref.document(user_id).get()
        if doc.exists:
            data = doc.to_dict()
            class FirestoreUser(UserMixin):
                pass
            user = FirestoreUser()
            user.id = doc.id
            user.username = data['username']
            user.email = data['email']
            user.password_hash = data['password_hash']
            user.is_tutor = data.get('is_tutor', False)
            return user
        return None

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
