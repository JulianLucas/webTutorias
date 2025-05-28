from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

bp = Blueprint('student', __name__, url_prefix='/student')

class SearchForm(FlaskForm):
    subject = StringField('Materia', validators=[DataRequired()])
    submit = SubmitField('Buscar')

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = SearchForm()
    tutors = []
    from app import db_firestore
    profiles_ref = db_firestore.collection('tutor_profiles')
    if form.validate_on_submit():
        subject = form.subject.data
        # Buscar perfiles de tutor cuyo campo subjects contenga el texto buscado
        tutors_query = profiles_ref.stream()
        tutors = []
        for doc in tutors_query:
            profile = doc.to_dict()
            if subject.lower() in profile.get('subjects', '').lower():
                profile['id'] = doc.id
                tutors.append(profile)
    else:
        # Traer todos los perfiles de tutor
        tutors = []
        for doc in profiles_ref.stream():
            profile = doc.to_dict()
            profile['id'] = doc.id
            tutors.append(profile)

    # Obtener las tutorías del estudiante desde Firestore
    from app import db_firestore
    bookings_ref = db_firestore.collection('bookings')
    bookings_query = bookings_ref.where('student_id', '==', current_user.id).stream()
    bookings = []
    for doc in bookings_query:
        booking = doc.to_dict()
        booking['id'] = doc.id
        bookings.append(booking)
    return render_template('student_dashboard.html', form=form, tutors=tutors, bookings=bookings)

@bp.route('/tutor/<string:tutor_id>', methods=['GET', 'POST'])
def tutor_profile(tutor_id):
    from app import db_firestore
    profiles_ref = db_firestore.collection('tutor_profiles')
    doc = profiles_ref.document(tutor_id).get()
    if not doc.exists:
        flash('Perfil de tutor no encontrado')
        return redirect(url_for('student.dashboard'))
    profile = doc.to_dict()
    profile['id'] = doc.id
    # Consultar reseñas desde Firestore
    reviews_ref = db_firestore.collection('reviews')
    reviews_query = reviews_ref.where('tutor_profile_id', '==', tutor_id).stream()
    reviews = []
    ratings = []
    for rdoc in reviews_query:
        review = rdoc.to_dict()
        review['id'] = rdoc.id
        reviews.append(review)
        ratings.append(review.get('rating', 0))
    avg_rating = sum(ratings) / len(ratings) if ratings else None
    return render_template('tutor_profile_detail.html', profile=profile, reviews=reviews, avg_rating=avg_rating)

@bp.route('/review/<string:tutor_id>', methods=['POST'])
@login_required
def add_review(tutor_id):
    from app import db_firestore
    form = ReviewForm()
    if form.validate_on_submit():
        review_data = {
            'tutor_profile_id': tutor_id,
            'student_id': current_user.id,
            'rating': form.rating.data,
            'comment': form.comment.data
        }
        db_firestore.collection('reviews').add(review_data)
        flash('Reseña agregada')
    return redirect(url_for('student.tutor_profile', tutor_id=tutor_id))
