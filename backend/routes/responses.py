from flask import request, jsonify
from routes import responses_bp
from models import db, AutoResponse, Message, Comment

@responses_bp.route('', methods=['GET', 'OPTIONS'])
@responses_bp.route('/', methods=['GET', 'OPTIONS'])
def get_responses():
    """Récupérer toutes les réponses"""
    if request.method == 'OPTIONS':
        return '', 200
    
    responses = AutoResponse.query.order_by(AutoResponse.priority.desc()).all()
    return jsonify([{
        'id': r.id,
        'trigger_keyword': r.trigger_keyword,
        'response_text': r.response_text,
        'response_type': r.response_type,
        'is_active': r.is_active,
        'priority': r.priority,
        'created_at': r.created_at.isoformat()
    } for r in responses])

@responses_bp.route('', methods=['POST'])
@responses_bp.route('/', methods=['POST'])
def create_response():
    """Créer une nouvelle réponse"""
    data = request.get_json()
    
    new_response = AutoResponse(
        trigger_keyword=data['trigger_keyword'],
        response_text=data['response_text'],
        response_type=data.get('response_type', 'both'),
        priority=data.get('priority', 0),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(new_response)
    db.session.commit()
    
    return jsonify({
        'message': 'Réponse créée avec succès',
        'id': new_response.id
    }), 201

@responses_bp.route('/<int:response_id>', methods=['PUT'])
def update_response(response_id):
    """Mettre à jour une réponse"""
    response = AutoResponse.query.get_or_404(response_id)
    data = request.get_json()
    
    response.trigger_keyword = data.get('trigger_keyword', response.trigger_keyword)
    response.response_text = data.get('response_text', response.response_text)
    response.response_type = data.get('response_type', response.response_type)
    response.is_active = data.get('is_active', response.is_active)
    response.priority = data.get('priority', response.priority)
    
    db.session.commit()
    
    return jsonify({'message': 'Réponse mise à jour avec succès'}), 200

@responses_bp.route('/<int:response_id>', methods=['DELETE'])
def delete_response(response_id):
    """Supprimer une réponse"""
    response = AutoResponse.query.get_or_404(response_id)
    db.session.delete(response)
    db.session.commit()
    return jsonify({'message': 'Réponse supprimée avec succès'}), 200

@responses_bp.route('/messages', methods=['GET'])
def get_messages():
    """Récupérer l'historique des messages"""
    limit = request.args.get('limit', 100, type=int)
    messages = Message.query.order_by(Message.timestamp.desc()).limit(limit).all()
    
    return jsonify([{
        'id': m.id,
        'message_id': m.message_id,
        'sender_id': m.sender_id,
        'sender_name': m.sender_name,
        'message_text': m.message_text,
        'response_sent': m.response_sent,
        'is_automated': m.is_automated,
        'timestamp': m.timestamp.isoformat()
    } for m in messages])

@responses_bp.route('/comments', methods=['GET'])
def get_comments():
    """Récupérer l'historique des commentaires"""
    limit = request.args.get('limit', 100, type=int)
    comments = Comment.query.order_by(Comment.timestamp.desc()).limit(limit).all()
    
    return jsonify([{
        'id': c.id,
        'comment_id': c.comment_id,
        'post_id': c.post_id,
        'user_id': c.user_id,
        'user_name': c.user_name,
        'comment_text': c.comment_text,
        'response_sent': c.response_sent,
        'is_automated': c.is_automated,
        'timestamp': c.timestamp.isoformat()
    } for c in comments])

@responses_bp.route('/stats', methods=['GET'])
def get_stats():
    """Obtenir les statistiques"""
    total_responses = AutoResponse.query.count()
    active_responses = AutoResponse.query.filter_by(is_active=True).count()
    total_messages = Message.query.count()
    total_comments = Comment.query.count()
    automated_messages = Message.query.filter_by(is_automated=True).count()
    automated_comments = Comment.query.filter_by(is_automated=True).count()
    
    return jsonify({
        'total_responses': total_responses,
        'active_responses': active_responses,
        'total_messages': total_messages,
        'total_comments': total_comments,
        'automated_messages': automated_messages,
        'automated_comments': automated_comments
    })