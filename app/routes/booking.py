from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

bp = Blueprint('booking', __name__, url_prefix='/booking')

class BookingForm(FlaskForm):
    subject = StringField('Materia', validators=[DataRequired()])
    datetime = StringField('Fecha y Hora', validators=[DataRequired()])
    submit = SubmitField('Solicitar Tutoría')

@bp.route('/request/<string:tutor_id>', methods=['GET', 'POST'])
@login_required
def request_booking(tutor_id):
    from app import db_firestore
    form = BookingForm()
    tutor_profile = TutorProfile.query.get_or_404(tutor_id)
    if form.validate_on_submit():
        # Generar nueva tutoría en Firestore
        booking_data = {
            'tutor_profile_id': tutor_profile.id,
            'student_id': current_user.id,
            'subject': form.subject.data,
            'datetime': form.datetime.data,
            'status': 'pendiente'
        }
        doc_ref = db_firestore.collection('bookings').add(booking_data)
        flash('Solicitud de tutoría enviada')
        return redirect(url_for('student.dashboard'))
    return render_template('booking_request.html', form=form, tutor_profile=tutor_profile)


@bp.route('/confirm/<string:booking_id>')
@login_required
def confirm_booking(booking_id):
    from app import db_firestore
    # Buscar booking en Firestore por ID
    bookings_ref = db_firestore.collection('bookings')
    docs = bookings_ref.where('__name__', '==', str(booking_id)).stream()
    booking_doc = next(docs, None)
    if booking_doc:
        booking = booking_doc.to_dict()
        # Verificar que el usuario es el tutor asignado
        from ..models import TutorProfile
        tutor_profile = TutorProfile.query.get(booking['tutor_profile_id'])
        if current_user.is_tutor and tutor_profile and tutor_profile.user_id == current_user.id:
            bookings_ref.document(booking_doc.id).update({'status': 'confirmada'})
            flash('Tutoría confirmada')
    return redirect(url_for('tutor.dashboard'))


@bp.route('/video/<string:booking_id>')
@login_required
def video_call(booking_id):
    from app import db_firestore
    # Buscar booking en Firestore por ID
    bookings_ref = db_firestore.collection('bookings')
    docs = bookings_ref.where('__name__', '==', str(booking_id)).stream()
    booking_doc = next(docs, None)
    if not booking_doc:
        flash('Tutoría no encontrada')
        return redirect(url_for('student.dashboard'))
    booking = booking_doc.to_dict()
    jitsi_url = f'https://meet.jit.si/tutoria_{booking_id}'
    return render_template('video_call.html', jitsi_url=jitsi_url, booking=booking)

