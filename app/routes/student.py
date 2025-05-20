from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from ..models import db, TutorProfile, Booking
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
    if form.validate_on_submit():
        subject = form.subject.data.lower()
        tutors = TutorProfile.query.filter(TutorProfile.subjects.ilike(f'%{subject}%')).all()
    else:
        tutors = TutorProfile.query.all()
    return render_template('student_dashboard.html', form=form, tutors=tutors)
