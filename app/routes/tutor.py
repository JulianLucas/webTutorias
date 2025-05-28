from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

bp = Blueprint('tutor', __name__, url_prefix='/tutor')

class TutorProfileForm(FlaskForm):
    bio = TextAreaField('Biografía', validators=[DataRequired()])
    subjects = StringField('Materias (separadas por coma)', validators=[DataRequired()])
    availability = StringField('Disponibilidad (ej: Lunes 10-12, Martes 14-16)', validators=[DataRequired()])
    submit = SubmitField('Guardar')

@bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_tutor:
        return redirect(url_for('student.dashboard'))
    # Obtener perfil del tutor desde Firestore
    from app import db_firestore
    profiles_ref = db_firestore.collection('tutor_profiles')
    existing = list(profiles_ref.where('user_id', '==', current_user.id).stream())
    profile_doc = existing[0] if existing else None
    profile = profile_doc.to_dict() if profile_doc else None
    if profile:
        profile['id'] = profile_doc.id
    # Consultar las tutorías del tutor desde Firestore
    bookings = []
    if profile:
        bookings_ref = db_firestore.collection('bookings')
        bookings_query = bookings_ref.where('tutor_profile_id', '==', profile['id']).stream()
        for doc in bookings_query:
            booking = doc.to_dict()
            booking['id'] = doc.id
            bookings.append(booking)
    return render_template('tutor_dashboard.html', profile=profile, bookings=bookings)


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    from app import db_firestore
    form = TutorProfileForm()
    profiles_ref = db_firestore.collection('tutor_profiles')
    # Buscar perfil por user_id
    existing = list(profiles_ref.where('user_id', '==', current_user.id).stream())
    profile_doc = existing[0] if existing else None
    profile = profile_doc.to_dict() if profile_doc else None
    if form.validate_on_submit():
        profile_data = {
            'user_id': current_user.id,
            'bio': form.bio.data,
            'subjects': form.subjects.data,
            'availability': form.availability.data
        }
        if profile_doc:
            profiles_ref.document(profile_doc.id).set(profile_data)
        else:
            profiles_ref.add(profile_data)
        flash('Perfil actualizado')
        return redirect(url_for('tutor.dashboard'))
    if profile:
        form.bio.data = profile.get('bio', '')
        form.subjects.data = profile.get('subjects', '')
        form.availability.data = profile.get('availability', '')
    return render_template('tutor_profile.html', form=form, profile=profile)
