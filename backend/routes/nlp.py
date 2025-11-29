"""
Routes API NLP - MESSAGES UNIQUEMENT
Compatible avec la structure messages only
"""

from flask import Blueprint, request, jsonify
from services.response_service import ResponseService
from models import Message, db

nlp_bp = Blueprint('nlp', __name__)

@nlp_bp.route('/analyze', methods=['POST'])
def analyze_text():
    """
    Analyser un texte avec NLP
    POST /api/nlp/analyze
    Body: {"text": "Message à analyser"}
    """
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'Texte requis'}), 400
    
    try:
        analysis = ResponseService.analyze_message_details(text)
        return jsonify({
            'success': True,
            'analysis': analysis
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Erreur d\'analyse: {str(e)}'
        }), 500


@nlp_bp.route('/test-response', methods=['POST'])
def test_response():
    """
    Tester une réponse pour un message donné
    POST /api/nlp/test-response
    Body: {"message": "Message de test"}
    """
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'Message requis'}), 400
    
    try:
        # Analyser le message
        analysis = ResponseService.analyze_message_details(message)
        
        # Trouver la réponse
        response_text = ResponseService.find_matching_response(message, 'message')
        
        if not response_text:
            response_text = ResponseService.get_default_response()
            matched = False
        else:
            matched = True
        
        return jsonify({
            'success': True,
            'input': {
                'message': message,
                'type': 'message'
            },
            'analysis': analysis,
            'response': {
                'text': response_text,
                'matched': matched
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': f'Erreur de test: {str(e)}'
        }), 500


@nlp_bp.route('/conversation-insights', methods=['GET'])
def get_conversation_insights():
    """
    Obtenir des insights sur les conversations récentes - MESSAGES UNIQUEMENT
    GET /api/nlp/conversation-insights?limit=50
    """
    limit = request.args.get('limit', 50, type=int)
    
    try:
        # Récupérer uniquement les messages
        messages = Message.query.order_by(
            Message.timestamp.desc()
        ).limit(limit).all()
        
        messages_data = [{
            'message_text': m.message_text,
            'type': 'message',
            'timestamp': m.timestamp.isoformat()
        } for m in messages if m.message_text]
        
        # Analyser les conversations
        insights = ResponseService.get_conversation_insights(messages_data)
        
        return jsonify({
            'success': True,
            'insights': insights,
            'analyzed_count': len(messages_data),
            'feature': 'messages_only'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': f'Erreur d\'analyse: {str(e)}'
        }), 500


@nlp_bp.route('/sentiment-stats', methods=['GET'])
def get_sentiment_stats():
    """
    Statistiques de sentiment sur les messages - MESSAGES UNIQUEMENT
    GET /api/nlp/sentiment-stats?days=7
    """
    from datetime import datetime, timedelta
    
    days = request.args.get('days', 7, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    try:
        # Messages récents uniquement
        messages = Message.query.filter(
            Message.timestamp >= start_date
        ).all()
        
        # Analyser les sentiments
        sentiment_counts = {
            'positif': 0,
            'negatif': 0,
            'neutre': 0
        }
        
        all_items = []
        
        for msg in messages:
            if msg.message_text:
                try:
                    analysis = ResponseService.analyze_message_details(msg.message_text)
                    sentiment = analysis['sentiment']['sentiment']
                    sentiment_counts[sentiment] += 1
                    all_items.append({
                        'type': 'message',
                        'text': msg.message_text[:50] + '...' if len(msg.message_text) > 50 else msg.message_text,
                        'sentiment': sentiment,
                        'score': analysis['sentiment']['score'],
                        'timestamp': msg.timestamp.isoformat()
                    })
                except:
                    continue
        
        total = sum(sentiment_counts.values())
        
        # Calculer les pourcentages
        percentages = {
            key: round((count / total * 100) if total > 0 else 0, 1)
            for key, count in sentiment_counts.items()
        }
        
        return jsonify({
            'success': True,
            'period': f'{days} jours',
            'total_analyzed': total,
            'sentiment_counts': sentiment_counts,
            'sentiment_percentages': percentages,
            'recent_items': sorted(
                all_items,
                key=lambda x: x['timestamp'],
                reverse=True
            )[:20],
            'feature': 'messages_only'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': f'Erreur de statistiques: {str(e)}'
        }), 500


@nlp_bp.route('/intents-stats', methods=['GET'])
def get_intents_stats():
    """
    Statistiques sur les intentions détectées - MESSAGES UNIQUEMENT
    GET /api/nlp/intents-stats?days=7
    """
    from datetime import datetime, timedelta
    from collections import Counter
    
    days = request.args.get('days', 7, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    try:
        # Récupérer les messages récents
        messages = Message.query.filter(
            Message.timestamp >= start_date
        ).all()
        
        # Analyser les intentions
        intents = []
        
        for msg in messages:
            if msg.message_text:
                try:
                    analysis = ResponseService.analyze_message_details(msg.message_text)
                    intents.append(analysis['intent'])
                except:
                    continue
        
        # Compter les intentions
        intent_counts = Counter(intents)
        
        # Formater les résultats
        intent_stats = [
            {
                'intent': intent,
                'count': count,
                'percentage': round((count / len(intents) * 100) if intents else 0, 1)
            }
            for intent, count in intent_counts.most_common()
        ]
        
        return jsonify({
            'success': True,
            'period': f'{days} jours',
            'total_analyzed': len(intents),
            'intent_stats': intent_stats,
            'top_3_intents': [item['intent'] for item in intent_stats[:3]],
            'feature': 'messages_only'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': f'Erreur de statistiques: {str(e)}'
        }), 500


@nlp_bp.route('/response-quality', methods=['GET'])
def get_response_quality():
    """
    Évaluer la qualité des réponses automatiques - MESSAGES UNIQUEMENT
    GET /api/nlp/response-quality?days=7
    """
    from datetime import datetime, timedelta
    
    days = request.args.get('days', 7, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    try:
        # Messages automatiques
        auto_messages = Message.query.filter(
            Message.timestamp >= start_date,
            Message.is_automated == True
        ).all()
        
        total_auto = len(auto_messages)
        
        # Analyser la satisfaction (basée sur les réponses reçues)
        positive_responses = 0
        negative_responses = 0
        
        for msg in auto_messages:
            if msg.response_sent:
                try:
                    analysis = ResponseService.analyze_message_details(msg.response_sent)
                    if analysis['sentiment']['sentiment'] == 'positif':
                        positive_responses += 1
                    elif analysis['sentiment']['sentiment'] == 'negatif':
                        negative_responses += 1
                except:
                    continue
        
        satisfaction_rate = round(
            (positive_responses / total_auto * 100) if total_auto > 0 else 0,
            1
        )
        
        return jsonify({
            'success': True,
            'period': f'{days} jours',
            'total_automated_responses': total_auto,
            'positive_responses': positive_responses,
            'negative_responses': negative_responses,
            'satisfaction_rate': satisfaction_rate,
            'quality_score': satisfaction_rate / 100,
            'feature': 'messages_only'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': f'Erreur d\'évaluation: {str(e)}'
        }), 500