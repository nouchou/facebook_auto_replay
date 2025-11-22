// URL de base de l'API - utilise la variable d'environnement ou localhost en développement
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

console.log('🌐 API URL:', API_BASE_URL); // Pour déboguer

class ApiService {
  // Helper pour obtenir le token
  getToken() {
    return localStorage.getItem('token');
  }

  // Helper pour les requêtes
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = this.getToken();
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      console.log(`📡 Request: ${options.method || 'GET'} ${url}`);
      
      const response = await fetch(url, config);
      
      // Si le token est invalide, rediriger vers login
      if (response.status === 401) {
        console.warn('⚠️ Token invalide ou expiré');
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        throw new Error('Session expirée. Veuillez vous reconnecter.');
      }

      // Vérifier si la réponse est OK
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({
          error: 'Erreur de connexion au serveur'
        }));
        throw new Error(errorData.error || errorData.message || `Erreur HTTP ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ Response:', data);
      return data;

    } catch (error) {
      console.error('❌ API Error:', error);
      
      // Si c'est une erreur réseau
      if (error.message === 'Failed to fetch' || error.name === 'TypeError') {
        throw new Error('Impossible de se connecter au serveur. Vérifiez votre connexion internet.');
      }
      
      throw error;
    }
  }

  // ==========================================
  // AUTHENTIFICATION
  // ==========================================
  
  async login(username, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  async verifyToken(token) {
    return this.request('/auth/verify', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  // ==========================================
  // RÉPONSES AUTOMATIQUES
  // ==========================================
  
  async getResponses() {
    return this.request('/responses');
  }

  async createResponse(data) {
    return this.request('/responses', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateResponse(id, data) {
    return this.request(`/responses/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteResponse(id) {
    return this.request(`/responses/${id}`, {
      method: 'DELETE',
    });
  }

  // ==========================================
  // MESSAGES ET COMMENTAIRES
  // ==========================================
  
  async getMessages(limit = 100) {
    return this.request(`/responses/messages?limit=${limit}`);
  }

  async getComments(limit = 100) {
    return this.request(`/responses/comments?limit=${limit}`);
  }

  // ==========================================
  // STATISTIQUES
  // ==========================================
  
  async getStats() {
    return this.request('/responses/stats');
  }

  // ==========================================
  // PAGES FACEBOOK
  // ==========================================
  
  async getPages() {
    return this.request('/facebook/pages');
  }

  async connectPage(data) {
    return this.request('/facebook/pages', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async disconnectPage(pageId) {
    return this.request(`/facebook/pages/${pageId}`, {
      method: 'DELETE',
    });
  }

  async togglePage(pageId) {
    return this.request(`/facebook/pages/${pageId}/toggle`, {
      method: 'PUT',
    });
  }

  async testConnection(accessToken) {
    return this.request('/facebook/test-connection', {
      method: 'POST',
      body: JSON.stringify({ access_token: accessToken }),
    });
  }

  // ==========================================
  // 🆕 NOUVELLES FONCTIONNALITÉS NLP
  // ==========================================

  /**
   * Analyser un texte avec NLP
   * @param {string} text - Texte à analyser
   * @returns {Promise} Résultat de l'analyse (intent, sentiment, tokens)
   */
  async analyzeText(text) {
    return this.request('/nlp/analyze', {
      method: 'POST',
      body: JSON.stringify({ text }),
    });
  }

  /**
   * Tester une réponse automatique
   * @param {string} message - Message à tester
   * @param {string} type - Type ('message', 'comment', 'both')
   * @returns {Promise} Réponse qui serait envoyée + analyse
   */
  async testResponse(message, type = 'both') {
    return this.request('/nlp/test-response', {
      method: 'POST',
      body: JSON.stringify({ message, type }),
    });
  }

  /**
   * Obtenir des insights sur les conversations
   * @param {number} limit - Nombre de messages à analyser (défaut: 50)
   * @param {string} type - Type ('messages', 'comments', 'all')
   * @returns {Promise} Insights de conversation (satisfaction, sentiments, intentions)
   */
  async getConversationInsights(limit = 50, type = 'all') {
    return this.request(`/nlp/conversation-insights?limit=${limit}&type=${type}`);
  }

  /**
   * Obtenir les statistiques de sentiment
   * @param {number} days - Nombre de jours à analyser (défaut: 7)
   * @returns {Promise} Distribution des sentiments (positif/négatif/neutre)
   */
  async getSentimentStats(days = 7) {
    return this.request(`/nlp/sentiment-stats?days=${days}`);
  }

  /**
   * Obtenir les statistiques d'intentions
   * @param {number} days - Nombre de jours à analyser (défaut: 7)
   * @returns {Promise} Intentions les plus fréquentes
   */
  async getIntentsStats(days = 7) {
    return this.request(`/nlp/intents-stats?days=${days}`);
  }

  /**
   * Obtenir la qualité des réponses automatiques
   * @param {number} days - Nombre de jours à analyser (défaut: 7)
   * @returns {Promise} Taux de satisfaction et qualité
   */
  async getResponseQuality(days = 7) {
    return this.request(`/nlp/response-quality?days=${days}`);
  }

  // ==========================================
  // SANTÉ DE L'API
  // ==========================================
  
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL.replace('/api', '')}/health`);
      return response.ok;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }
}

export const api = new ApiService();
export default api;