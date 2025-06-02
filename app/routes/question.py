from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db_firestore
import requests
import os
import logging
logger = logging.getLogger("webtutorias-debug")
logging.basicConfig(level=logging.WARNING)

bp = Blueprint('question', __name__, url_prefix='/question')

N8N_WEBHOOK_URL = "https://juli4n.app.n8n.cloud/webhook-test/80b9035a-4634-4ecb-a421-531d97b4979f"

from app import csrf

@bp.route('/ask', methods=['POST'])
@csrf.exempt
@login_required
def ask_question():
    logger.warning(f"HEADERS: {dict(request.headers)}")
    logger.warning(f"RAW DATA: {request.data}")
    data = request.get_json(force=True, silent=True)
    logger.warning(f"JSON (forced): {data}")
    pregunta = data.get('pregunta') if data else None
    if not pregunta:
        return jsonify({'error': 'La pregunta es obligatoria'}), 400
    pregunta_data = {
        'pregunta': pregunta,
        'estudiante_id': current_user.id,
        'email': getattr(current_user, 'email', None),
        'respuesta': None,
        'estado': 'pendiente'
    }
    doc_ref = db_firestore.collection('preguntas').add(pregunta_data)
    pregunta_id = doc_ref[1].id
    # Enviar a n8n
    try:
        import requests
        requests.post(N8N_WEBHOOK_URL, json={
            'pregunta': pregunta,
            'pregunta_id': pregunta_id,
            'estudiante_id': current_user.id,
            'email': getattr(current_user, 'email', None)
        }, timeout=5)
    except Exception as e:
        logger.warning(f"Error enviando a n8n: {e}")
    return jsonify({'status': 'ok', 'pregunta_id': pregunta_id})

@bp.route('/respuesta', methods=['POST'])
@csrf.exempt
def recibir_respuesta():
    data = request.json
    pregunta_id = data.get('pregunta_id')
    respuesta = data.get('respuesta')
    if not pregunta_id or not respuesta:
        return jsonify({'error': 'Faltan datos'}), 400
    pregunta_ref = db_firestore.collection('preguntas').document(pregunta_id)
    if not pregunta_ref.get().exists:
        return jsonify({'error': 'Pregunta no encontrada'}), 404
    pregunta_ref.update({'respuesta': respuesta, 'estado': 'respondida'})
    return jsonify({'status': 'respuesta guardada'})
