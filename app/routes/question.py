from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db_firestore
import requests
import os

bp = Blueprint('question', __name__, url_prefix='/question')

N8N_WEBHOOK_URL = "https://juli4n.app.n8n.cloud/webhook-test/80b9035a-4634-4ecb-a421-531d97b4979f"

@bp.route('/ask', methods=['POST'])
@login_required
def ask_question():
    data = request.json
    pregunta = data.get('pregunta')
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
        requests.post(N8N_WEBHOOK_URL, json={
            'pregunta': pregunta,
            'pregunta_id': pregunta_id,
            'estudiante_id': current_user.id,
            'email': getattr(current_user, 'email', None)
        }, timeout=5)
    except Exception as e:
        # No es crítico si falla el webhook, pero lo registramos
        print(f"Error enviando a n8n: {e}")
    return jsonify({'status': 'ok', 'pregunta_id': pregunta_id})

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
