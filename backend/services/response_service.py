"""
Service de réponses automatiques avec NLP - VERSION INTÉGRÉE
Remplace le fichier services/response_service.py existant
"""

import re
import string
from typing import List, Dict, Optional
from difflib import SequenceMatcher
from models import db, AutoResponse

class NLPChatbot:
    """Chatbot avec capacités de traitement du langage naturel"""
    
    def __init__(self):
        # Stopwords français
        self.stopwords = {
            'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'à', 'au',
            'et', 'ou', 'mais', 'donc', 'car', 'si', 'que', 'qui', 'quoi',
            'ce', 'cette', 'mon', 'ma', 'mes', 'je', 'tu', 'il', 'elle',
            'nous', 'vous', 'ils', 'elles', 'en', 'y', 'dans', 'sur', 'est'
        }
        
        # Patterns d'intentions
        self.intent_patterns = {
            'salutation': r'\b(bonjour|bonsoir|salut|hello|hi|coucou)\b',
            'question_prix': r'\b(prix|coût|combien|tarif)\b',
            'disponibilite': r'\b(disponible|dispo|stock|reste)\b',
            'demande_info': r'\b(info|information|comment|pourquoi|détail)\b',
            'commande': r'\b(commander|acheter|prendre|réserver|veux)\b',
            'probleme': r'\b(problème|souci|erreur|aide|marche pas)\b',
            'remerciement': r'\b(merci|thanks)\b',
            'contact': r'\b(contact|téléphone|email|appeler)\b',
            'livraison': r'\b(livraison|livrer|délai|expédition)\b'
        }
        
        # Mots de sentiment
        self.sentiment_words = {
            'positif': ['super', 'génial', 'excellent', 'parfait', 'bien', 
                       'bon', 'content', 'satisfait', 'merci', 'top'],
            'negatif': ['mauvais', 'nul', 'horrible', 'problème', 'erreur',
                       'déçu', 'arnaque', 'pourri', 'pas content']
        }
    
    def preprocess_text(self, text: str) -> str:
        """Nettoyage et normalisation du texte"""
        if not text:
            return ""
        text = text.lower().strip()
        text = re.sub(r'[!?]{2,}', '!', text)
        text = ' '.join(text.split())
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """Découper le texte en tokens (mots)"""
        text = text.translate(str.maketrans('', '', string.punctuation))
        tokens = text.lower().split()
        return [t for t in tokens if t not in self.stopwords and len(t) > 2]
    
    def extract_intent(self, text: str) -> str:
        """Reconnaître l'intention du message"""
        text_lower = text.lower()
        for intent, pattern in self.intent_patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                return intent
        return 'general'
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyser le sentiment du message"""
        tokens = self.tokenize(text)
        
        positive = sum(1 for word in tokens if word in self.sentiment_words['positif'])
        negative = sum(1 for word in tokens if word in self.sentiment_words['negatif'])
        
        if positive > negative:
            sentiment = 'positif'
            score = positive / (positive + negative + 1)
        elif negative > positive:
            sentiment = 'negatif'
            score = negative / (positive + negative + 1)
        else:
            sentiment = 'neutre'
            score = 0.5
        
        return {
            'sentiment': sentiment,
            'score': score,
            'positive_words': positive,
            'negative_words': negative
        }
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculer la similarité entre deux textes (0-1)"""
        # Similarité de séquence
        seq_sim = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        
        # Similarité des tokens (Jaccard)
        tokens1 = set(self.tokenize(text1))
        tokens2 = set(self.tokenize(text2))
        
        if not tokens1 or not tokens2:
            return seq_sim
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        jaccard_sim = len(intersection) / len(union) if union else 0
        
        # Moyenne pondérée
        return (seq_sim * 0.4 + jaccard_sim * 0.6)
    
    def find_best_response(self, user_message: str, responses_db: List[Dict]) -> Optional[Dict]:
        """Trouver la meilleure réponse avec scoring NLP"""
        if not responses_db:
            return None
        
        processed_message = self.preprocess_text(user_message)
        active_responses = [r for r in responses_db if r.get('is_active', True)]
        
        if not active_responses:
            return None
        
        scored_responses = []
        
        for response in active_responses:
            keyword = response.get('trigger_keyword', '')
            priority = response.get('priority', 0)
            
            # Calculer les scores
            similarity = self.calculate_similarity(processed_message, keyword)
            
            # Vérifier correspondance exacte des mots-clés (comme l'ancien système)
            keywords = [k.strip().lower() for k in keyword.split(',')]
            keyword_match = 0.0
            for kw in keywords:
                if kw in processed_message or re.search(r'\b' + re.escape(kw) + r'\b', processed_message):
                    keyword_match = 1.0
                    break
            
            # Score final pondéré
            final_score = (
                similarity * 0.5 +
                keyword_match * 0.4 +
                (priority / 100) * 0.1
            )
            
            scored_responses.append({
                'response': response,
                'score': final_score
            })
        
        # Trier par score décroissant
        scored_responses.sort(key=lambda x: x['score'], reverse=True)
        
        # Retourner si score suffisant
        best = scored_responses[0]
        return best['response'] if best['score'] >= 0.3 else None
    
    def analyze_message(self, message: str) -> Dict:
        """Analyse complète d'un message"""
        processed = self.preprocess_text(message)
        
        return {
            'original': message,
            'processed': processed,
            'tokens': self.tokenize(processed),
            'intent': self.extract_intent(message),
            'sentiment': self.analyze_sentiment(message),
            'word_count': len(message.split())
        }
    
    def generate_context_response(self, analysis: Dict, base_response: str) -> str:
        """Personnaliser la réponse selon le contexte"""
        sentiment = analysis['sentiment']['sentiment']
        intent = analysis['intent']
        
        # Préfixes selon sentiment
        prefix = ""
        if sentiment == 'negatif':
            prefix = "Je comprends votre préoccupation. "
        elif sentiment == 'positif':
            prefix = "Merci pour votre intérêt ! "
        
        # Suffixes selon intention
        suffixes = {
            'question_prix': " N'hésitez pas si vous avez d'autres questions.",
            'probleme': " Notre équipe est là pour vous aider.",
            'commande': " Nous traitons votre demande rapidement.",
            'contact': " Vous pouvez nous contacter directement."
        }
        
        suffix = suffixes.get(intent, " Merci pour votre message !")
        
        return f"{prefix}{base_response}{suffix}"


class ResponseService:
    """
    Service principal pour gérer les réponses automatiques
    Compatible avec l'ancien système + nouvelles fonctionnalités NLP
    """
    
    chatbot = NLPChatbot()
    
    @staticmethod
    def find_matching_response(message_text: str, response_type: str = 'message'):
        """
        Trouver une réponse correspondante basée sur les mots-clés
        VERSION AMÉLIORÉE avec NLP tout en gardant la compatibilité
        
        Args:
            message_text: Texte du message/commentaire
            response_type: 'message', 'comment', ou 'both'
        
        Returns:
            Texte de la réponse ou None
        """
        try:
            message_lower = message_text.lower()
            
            # Récupérer toutes les réponses actives triées par priorité
            responses = AutoResponse.query.filter_by(
                is_active=True
            ).filter(
                (AutoResponse.response_type == response_type) | 
                (AutoResponse.response_type == 'both')
            ).order_by(AutoResponse.priority.desc()).all()
            
            if not responses:
                return None
            
            # MÉTHODE 1: Recherche exacte (comme l'ancien système) - PRIORITAIRE
            for response in responses:
                keywords = response.trigger_keyword.lower().split(',')
                for keyword in keywords:
                    keyword = keyword.strip()
                    # Recherche exacte ou partielle
                    if keyword in message_lower or re.search(r'\b' + re.escape(keyword) + r'\b', message_lower):
                        # Analyser le message pour personnaliser
                        analysis = ResponseService.chatbot.analyze_message(message_text)
                        return ResponseService.chatbot.generate_context_response(
                            analysis,
                            response.response_text
                        )
            
            # MÉTHODE 2: Recherche par NLP si aucune correspondance exacte
            responses_dict = [{
                'id': r.id,
                'trigger_keyword': r.trigger_keyword,
                'response_text': r.response_text,
                'response_type': r.response_type,
                'is_active': r.is_active,
                'priority': r.priority
            } for r in responses]
            
            best_response = ResponseService.chatbot.find_best_response(
                message_text,
                responses_dict
            )
            
            if best_response:
                analysis = ResponseService.chatbot.analyze_message(message_text)
                return ResponseService.chatbot.generate_context_response(
                    analysis,
                    best_response['response_text']
                )
            
            return None
            
        except Exception as e:
            print(f"Erreur dans find_matching_response: {str(e)}")
            # En cas d'erreur, utiliser l'ancienne méthode simple
            message_lower = message_text.lower()
            responses = AutoResponse.query.filter_by(
                is_active=True
            ).filter(
                (AutoResponse.response_type == response_type) | 
                (AutoResponse.response_type == 'both')
            ).order_by(AutoResponse.priority.desc()).all()
            
            for response in responses:
                keywords = response.trigger_keyword.lower().split(',')
                for keyword in keywords:
                    keyword = keyword.strip()
                    if keyword in message_lower:
                        return response.response_text
            
            return None
    
    @staticmethod
    def get_default_response():
        """Réponse par défaut si aucune correspondance"""
        return "Merci pour votre message. Notre équipe vous répondra dans les plus brefs délais."
    
    @staticmethod
    def analyze_message_details(message_text: str) -> Dict:
        """
        Analyser un message en détail (pour dashboard/stats)
        NOUVELLE FONCTIONNALITÉ
        """
        return ResponseService.chatbot.analyze_message(message_text)
    
    @staticmethod
    def get_conversation_insights(messages: List[Dict]) -> Dict:
        """
        Obtenir des insights sur une conversation
        NOUVELLE FONCTIONNALITÉ
        """
        if not messages:
            return {
                'total_messages': 0,
                'average_sentiment': 'neutre',
                'main_intents': [],
                'satisfaction_score': 0.5
            }
        
        sentiments = []
        intents = []
        
        for msg in messages:
            try:
                analysis = ResponseService.chatbot.analyze_message(
                    msg.get('message_text', '')
                )
                sentiments.append(analysis['sentiment']['score'])
                intents.append(analysis['intent'])
            except:
                continue
        
        if not sentiments:
            return {
                'total_messages': len(messages),
                'average_sentiment': 'neutre',
                'main_intents': [],
                'satisfaction_score': 0.5
            }
        
        # Sentiment moyen
        avg_score = sum(sentiments) / len(sentiments)
        
        if avg_score > 0.6:
            avg_sentiment = 'positif'
        elif avg_score < 0.4:
            avg_sentiment = 'negatif'
        else:
            avg_sentiment = 'neutre'
        
        # Intentions principales
        from collections import Counter
        intent_counts = Counter(intents)
        main_intents = [i for i, _ in intent_counts.most_common(3)]
        
        return {
            'total_messages': len(messages),
            'average_sentiment': avg_sentiment,
            'sentiment_score': round(avg_score, 2),
            'main_intents': main_intents,
            'satisfaction_score': round(avg_score, 2)
        }