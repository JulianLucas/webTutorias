from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from ..models import db, TutorProfile, Booking
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
    profile = TutorProfile.query.filter_by(user_id=current_user.id).first()
    bookings = Booking.query.filter_by(tutor_profile_id=profile.id).all() if profile else []
    return render_template('tutor_dashboard.html', profile=profile, bookings=bookings)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if not current_user.is_tutor:
        return redirect(url_for('student.dashboard'))
    profile = TutorProfile.query.filter_by(user_id=current_user.id).first()
    form = TutorProfileForm(obj=profile)
    if form.validate_on_submit():
        if not profile:
            profile = TutorProfile(user_id=current_user.id)
            db.session.add(profile)
        profile.bio = form.bio.data
        profile.subjects = form.subjects.data
        profile.availability = form.availability.data
        db.session.commit()
        flash('Perfil actualizado')
        return redirect(url_for('tutor.dashboard'))
    return render_template('tutor_profile.html', form=form, profile=profile)
