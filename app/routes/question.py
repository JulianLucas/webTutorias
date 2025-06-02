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

@bp.route('/ask', methods=['POST'])
@login_required
def ask_question():
    logger.warning(f"HEADERS: {dict(request.headers)}")
    logger.warning(f"RAW DATA: {request.data}")
    data = request.get_json(force=True, silent=True)
    logger.warning(f"JSON (forced): {data}")
    # No procesamos ni guardamos la pregunta, solo respondemos éxito
    return jsonify({'status': 'ok', 'message': 'Pregunta recibida (dummy endpoint)'})

@bp.route('/respuesta', methods=['POST'])
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
