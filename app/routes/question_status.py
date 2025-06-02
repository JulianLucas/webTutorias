from flask import Blueprint, jsonify
from app import db_firestore

bp = Blueprint('question_status', __name__, url_prefix='/question')

@bp.route('/status/<string:pregunta_id>', methods=['GET'])
def question_status(pregunta_id):
    pregunta_ref = db_firestore.collection('preguntas').document(pregunta_id)
    doc = pregunta_ref.get()
    if not doc.exists:
        return jsonify({'error': 'Pregunta no encontrada'}), 404
    data = doc.to_dict()
    return jsonify({
        'pregunta': data.get('pregunta'),
        'respuesta': data.get('respuesta'),
        'estado': data.get('estado')
    })
