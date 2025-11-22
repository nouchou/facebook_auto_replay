import React, { useState, useEffect } from 'react';
import { Brain, TrendingUp, MessageSquare, Smile, Frown, Meh } from 'lucide-react';
import { api } from '../services/api';

/**
 * Composant Dashboard NLP
 * À ajouter dans votre Dashboard.jsx ou comme page séparée
 */
const NLPDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [insights, setInsights] = useState(null);
  const [sentiments, setSentiments] = useState(null);
  const [intents, setIntents] = useState(null);
  const [quality, setQuality] = useState(null);

  useEffect(() => {
    fetchNLPData();
  }, []);

  const fetchNLPData = async () => {
    try {
      setLoading(true);
      
      const [insightsData, sentimentsData, intentsData, qualityData] = await Promise.all([
        api.getConversationInsights(100, 'all'),
        api.getSentimentStats(7),
        api.getIntentsStats(7),
        api.getResponseQuality(7)
      ]);

      setInsights(insightsData.insights);
      setSentiments(sentimentsData);
      setIntents(intentsData);
      setQuality(qualityData);
    } catch (error) {
      console.error('Erreur lors du chargement des données NLP:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Analyse NLP en cours...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Brain className="w-8 h-8 text-blue-600" />
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Analyse NLP</h2>
            <p className="text-sm text-gray-500">Intelligence artificielle </p>
          </div>
        </div>
        <button
          onClick={fetchNLPData}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Actualiser
        </button>
      </div>

      {/* Cartes de statistiques principales */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Score de satisfaction */}
        <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg shadow-sm border border-green-200">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="w-6 h-6 text-green-600" />
            <span className="text-2xl font-bold text-green-600">
              {insights?.satisfaction_score ? (insights.satisfaction_score * 100).toFixed(0) : 0}%
            </span>
          </div>
          <h3 className="text-sm font-medium text-green-900">Score de Satisfaction</h3>
          <p className="text-xs text-green-700 mt-1">Basé sur {insights?.total_messages || 0} messages</p>
        </div>

        {/* Messages analysés */}
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg shadow-sm border border-blue-200">
          <div className="flex items-center justify-between mb-2">
            <MessageSquare className="w-6 h-6 text-blue-600" />
            <span className="text-2xl font-bold text-blue-600">
              {sentiments?.total_analyzed || 0}
            </span>
          </div>
          <h3 className="text-sm font-medium text-blue-900">Messages Analysés</h3>
          <p className="text-xs text-blue-700 mt-1">7 derniers jours</p>
        </div>

        {/* Réponses automatiques */}
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-lg shadow-sm border border-purple-200">
          <div className="flex items-center justify-between mb-2">
            <Brain className="w-6 h-6 text-purple-600" />
            <span className="text-2xl font-bold text-purple-600">
              {quality?.total_automated_responses || 0}
            </span>
          </div>
          <h3 className="text-sm font-medium text-purple-900">Réponses Auto</h3>
          <p className="text-xs text-purple-700 mt-1">Qualité: {quality?.satisfaction_rate || 0}%</p>
        </div>

        {/* Sentiment général */}
        <div className={`p-6 rounded-lg shadow-sm border ${
          insights?.average_sentiment === 'positif' 
            ? 'bg-gradient-to-br from-green-50 to-green-100 border-green-200'
            : insights?.average_sentiment === 'negatif'
            ? 'bg-gradient-to-br from-red-50 to-red-100 border-red-200'
            : 'bg-gradient-to-br from-gray-50 to-gray-100 border-gray-200'
        }`}>
          <div className="flex items-center justify-between mb-2">
            {insights?.average_sentiment === 'positif' ? (
              <Smile className="w-6 h-6 text-green-600" />
            ) : insights?.average_sentiment === 'negatif' ? (
              <Frown className="w-6 h-6 text-red-600" />
            ) : (
              <Meh className="w-6 h-6 text-gray-600" />
            )}
            <span className={`text-sm font-semibold capitalize ${
              insights?.average_sentiment === 'positif' ? 'text-green-600'
              : insights?.average_sentiment === 'negatif' ? 'text-red-600'
              : 'text-gray-600'
            }`}>
              {insights?.average_sentiment || 'Neutre'}
            </span>
          </div>
          <h3 className={`text-sm font-medium ${
            insights?.average_sentiment === 'positif' ? 'text-green-900'
            : insights?.average_sentiment === 'negatif' ? 'text-red-900'
            : 'text-gray-900'
          }`}>
            Sentiment Général
          </h3>
          <p className={`text-xs mt-1 ${
            insights?.average_sentiment === 'positif' ? 'text-green-700'
            : insights?.average_sentiment === 'negatif' ? 'text-red-700'
            : 'text-gray-700'
          }`}>
            Ambiance globale
          </p>
        </div>
      </div>

      {/* Distribution des sentiments */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Distribution des Sentiments</h3>
        
        <div className="space-y-4">
          {/* Positif */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Smile className="w-5 h-5 text-green-600" />
                <span className="text-sm font-medium text-gray-700">Positif</span>
              </div>
              <span className="text-sm font-semibold text-green-600">
                {sentiments?.sentiment_percentages?.positif || 0}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-green-500 h-3 rounded-full transition-all duration-500"
                style={{ width: `${sentiments?.sentiment_percentages?.positif || 0}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {sentiments?.sentiment_counts?.positif || 0} messages
            </p>
          </div>

          {/* Neutre */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Meh className="w-5 h-5 text-gray-600" />
                <span className="text-sm font-medium text-gray-700">Neutre</span>
              </div>
              <span className="text-sm font-semibold text-gray-600">
                {sentiments?.sentiment_percentages?.neutre || 0}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-gray-500 h-3 rounded-full transition-all duration-500"
                style={{ width: `${sentiments?.sentiment_percentages?.neutre || 0}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {sentiments?.sentiment_counts?.neutre || 0} messages
            </p>
          </div>

          {/* Négatif */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Frown className="w-5 h-5 text-red-600" />
                <span className="text-sm font-medium text-gray-700">Négatif</span>
              </div>
              <span className="text-sm font-semibold text-red-600">
                {sentiments?.sentiment_percentages?.negatif || 0}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-red-500 h-3 rounded-full transition-all duration-500"
                style={{ width: `${sentiments?.sentiment_percentages?.negatif || 0}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {sentiments?.sentiment_counts?.negatif || 0} messages
            </p>
          </div>
        </div>
      </div>

      {/* Intentions principales */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Intentions Principales</h3>
        
        <div className="space-y-3">
          {intents?.intent_stats?.slice(0, 5).map((intent, index) => (
            <div key={intent.intent} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <span className="flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-600 rounded-full font-semibold text-sm">
                  {index + 1}
                </span>
                <span className="text-sm font-medium text-gray-700 capitalize">
                  {intent.intent.replace('_', ' ')}
                </span>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-500">{intent.count} fois</span>
                <span className="text-sm font-semibold text-blue-600">{intent.percentage}%</span>
              </div>
            </div>
          ))}
        </div>

        {intents?.intent_stats?.length === 0 && (
          <p className="text-center text-gray-500 py-8">Aucune intention détectée pour le moment</p>
        )}
      </div>

      {/* Messages récents avec sentiment */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Messages Récents</h3>
        
        <div className="space-y-3">
          {sentiments?.recent_items?.slice(0, 10).map((item, index) => (
            <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
              <div className={`flex-shrink-0 mt-1 ${
                item.sentiment === 'positif' ? 'text-green-600'
                : item.sentiment === 'negatif' ? 'text-red-600'
                : 'text-gray-600'
              }`}>
                {item.sentiment === 'positif' ? (
                  <Smile className="w-5 h-5" />
                ) : item.sentiment === 'negatif' ? (
                  <Frown className="w-5 h-5" />
                ) : (
                  <Meh className="w-5 h-5" />
                )}
              </div>
              
              <div className="flex-1">
                <p className="text-sm text-gray-700">{item.text}</p>
                <div className="flex items-center space-x-3 mt-1">
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    item.type === 'message' 
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-purple-100 text-purple-700'
                  }`}>
                    {item.type === 'message' ? 'Message' : 'Commentaire'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(item.timestamp).toLocaleDateString('fr-FR')}
                  </span>
                  <span className={`text-xs font-medium ${
                    item.sentiment === 'positif' ? 'text-green-600'
                    : item.sentiment === 'negatif' ? 'text-red-600'
                    : 'text-gray-600'
                  }`}>
                    Score: {item.score.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {sentiments?.recent_items?.length === 0 && (
          <p className="text-center text-gray-500 py-8">Aucun message récent</p>
        )}
      </div>
    </div>
  );
};

export default NLPDashboard;