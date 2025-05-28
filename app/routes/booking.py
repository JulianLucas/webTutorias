from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

bp = Blueprint('booking', __name__, url_prefix='/booking')

class BookingForm(FlaskForm):
    subject = StringField('Materia', validators=[DataRequired()])
    horario = SelectField('Horario disponible', validators=[DataRequired()], choices=[])
    submit = SubmitField('Solicitar Tutoría')

@bp.route('/request/<string:tutor_id>', methods=['GET', 'POST'])
@login_required
def request_booking(tutor_id):
    from app import db_firestore
    profiles_ref = db_firestore.collection('tutor_profiles')
    doc = profiles_ref.document(tutor_id).get()
    if not doc.exists:
        flash('Perfil de tutor no encontrado')
        return redirect(url_for('student.dashboard'))
    tutor_profile = doc.to_dict()
    tutor_profile['id'] = doc.id
    # Obtener el nombre de usuario del tutor
    users_ref = db_firestore.collection('users')
    user_doc = users_ref.document(str(tutor_profile.get('user_id'))).get()
    tutor_profile['username'] = user_doc.to_dict().get('username', 'Tutor') if user_doc.exists else 'Tutor'
    # Obtener horarios disponibles del tutor
    disponibilidad = tutor_profile.get('availability', '')
    horarios = [h.strip() for h in disponibilidad.split(',') if h.strip()]
    # Excluir horarios ocupados
    bookings_ref = db_firestore.collection('bookings')
    bookings_query = bookings_ref.where('tutor_profile_id', '==', tutor_profile['id']).stream()
    horarios_ocupados = set()
    for bdoc in bookings_query:
        booking = bdoc.to_dict()
        if booking.get('status') in ('pendiente', 'confirmada'):
            horarios_ocupados.add(booking.get('datetime'))
    horarios_disponibles = [h for h in horarios if h not in horarios_ocupados]
    form = BookingForm()
    form.horario.choices = [(h, h) for h in horarios_disponibles]
    if form.validate_on_submit():
        # Validar que el horario esté en la disponibilidad del tutor
        horario_seleccionado = form.horario.data
        if horario_seleccionado not in horarios:
            flash('El horario seleccionado no está disponible para este tutor')
            return render_template('booking_request.html', form=form, tutor_profile=tutor_profile)
        # Generar nueva tutoría en Firestore
        booking_data = {
            'tutor_profile_id': tutor_profile['id'],
            'student_id': current_user.id,
            'subject': form.subject.data,
            'datetime': horario_seleccionado,
            'status': 'pendiente'
        }
        db_firestore.collection('bookings').add(booking_data)
        flash(f'Solicitud de tutoría enviada para el horario "{horario_seleccionado}" con el tutor {tutor_profile.get("username", "")}')
        return redirect(url_for('student.dashboard'))
    return render_template('booking_request.html', form=form, tutor_profile=tutor_profile)


@bp.route('/confirm/<string:booking_id>')
@login_required
def confirm_booking(booking_id):
    from app import db_firestore
    # Buscar booking en Firestore por ID
    bookings_ref = db_firestore.collection('bookings')
    booking_doc = bookings_ref.document(str(booking_id)).get()
    if booking_doc.exists:
        booking = booking_doc.to_dict()
        # Verificar que el usuario es el tutor asignado (por user_id en el perfil de tutor Firestore)
        profiles_ref = db_firestore.collection('tutor_profiles')
        tutor_profile_doc = profiles_ref.document(booking['tutor_profile_id']).get()
        if tutor_profile_doc.exists:
            tutor_profile = tutor_profile_doc.to_dict()
            if current_user.is_tutor and tutor_profile.get('user_id') == current_user.id:
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

