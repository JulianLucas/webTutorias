from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login_manager
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

bp = Blueprint('auth', __name__, url_prefix='/auth')

class RegisterForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repetir Contraseña', validators=[DataRequired(), EqualTo('password')])
    is_tutor = BooleanField('¿Eres tutor?')
    submit = SubmitField('Registrarse')

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    from app import db_firestore
    form = RegisterForm()
    if form.validate_on_submit():
        # Buscar usuario por username en Firestore
        users_ref = db_firestore.collection('users')
        existing = list(users_ref.where('username', '==', form.username.data).stream())
        if existing:
            flash('El usuario ya existe')
            return redirect(url_for('auth.register'))
        # Crear usuario en Firestore
        user_data = {
            'username': form.username.data,
            'email': form.email.data,
            'password_hash': generate_password_hash(form.password.data),
            'is_tutor': form.is_tutor.data
        }
        users_ref.add(user_data)
        flash('Registro exitoso. Ahora puedes iniciar sesión.')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    from app import db_firestore
    from flask_login import UserMixin
    form = LoginForm()
    if form.validate_on_submit():
        users_ref = db_firestore.collection('users')
        user_docs = list(users_ref.where('username', '==', form.username.data).stream())
        if user_docs:
            user_data = user_docs[0].to_dict()
            # Clase temporal para Flask-Login
            class FirestoreUser(UserMixin):
                pass
            user = FirestoreUser()
            user.id = user_docs[0].id
            user.username = user_data['username']
            user.email = user_data['email']
            user.password_hash = user_data['password_hash']
            user.is_tutor = user_data.get('is_tutor', False)
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Bienvenido, ' + user.username)
                return redirect(url_for('tutor.dashboard' if user.is_tutor else 'student.dashboard'))
        flash('Usuario o contraseña incorrectos')
    return render_template('login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión')
    return redirect(url_for('auth.login'))
