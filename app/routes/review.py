from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from flask_wtf import FlaskForm
from wtforms import IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange

bp = Blueprint('review', __name__, url_prefix='/review')

class ReviewForm(FlaskForm):
    rating = IntegerField('Calificación (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField('Comentario', validators=[DataRequired()])
    submit = SubmitField('Enviar reseña')

@bp.route('/add/<string:tutor_id>', methods=['GET', 'POST'])
@login_required
def add_review(tutor_id):
    from app import db_firestore
    form = ReviewForm()
    # Obtener perfil del tutor desde Firestore
    profiles_ref = db_firestore.collection('tutor_profiles')
    doc = profiles_ref.document(tutor_id).get()
    if not doc.exists:
        flash('Perfil de tutor no encontrado')
        return redirect(url_for('student.dashboard'))
    tutor_profile = doc.to_dict()
    tutor_profile['id'] = doc.id
    if form.validate_on_submit():
        review_data = {
            'tutor_profile_id': tutor_profile['id'],
            'student_id': current_user.id,
            'rating': form.rating.data,
            'comment': form.comment.data
        }
        db_firestore.collection('reviews').add(review_data)
        flash('Reseña enviada')
        return redirect(url_for('student.dashboard'))
    return render_template('add_review.html', form=form, tutor_profile=tutor_profile)
