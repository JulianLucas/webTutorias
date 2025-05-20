from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from ..models import db, TutorProfile, Booking
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

bp = Blueprint('booking', __name__, url_prefix='/booking')

class BookingForm(FlaskForm):
    subject = StringField('Materia', validators=[DataRequired()])
    datetime = StringField('Fecha y Hora', validators=[DataRequired()])
    submit = SubmitField('Solicitar Tutoría')

@bp.route('/request/<int:tutor_id>', methods=['GET', 'POST'])
@login_required
def request_booking(tutor_id):
    form = BookingForm()
    tutor_profile = TutorProfile.query.get_or_404(tutor_id)
    if form.validate_on_submit():
        booking = Booking(
            tutor_profile_id=tutor_profile.id,
            student_id=current_user.id,
            subject=form.subject.data,
            datetime=form.datetime.data,
            status='pendiente'
        )
        db.session.add(booking)
        db.session.commit()
        flash('Solicitud de tutoría enviada')
        return redirect(url_for('student.dashboard'))
    return render_template('booking_request.html', form=form, tutor_profile=tutor_profile)

@bp.route('/confirm/<int:booking_id>')
@login_required
def confirm_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if current_user.is_tutor and booking.tutor_profile.user_id == current_user.id:
        booking.status = 'confirmada'
        db.session.commit()
        flash('Tutoría confirmada')
    return redirect(url_for('tutor.dashboard'))

@bp.route('/video/<int:booking_id>')
@login_required
def video_call(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    # Enlace a Jitsi Meet usando el ID de la tutoría como room name
    jitsi_url = f'https://meet.jit.si/tutoria_{booking.id}'
    return render_template('video_call.html', jitsi_url=jitsi_url, booking=booking)
