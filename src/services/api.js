const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

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
      const response = await fetch(url, config);
      
      // Si le token est invalide, rediriger vers login
      if (response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        throw new Error('Session expirée. Veuillez vous reconnecter.');
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.message || 'Une erreur est survenue');
      }

      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Authentification
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

  // Réponses automatiques
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

  // Messages
  async getMessages(limit = 100) {
    return this.request(`/responses/messages?limit=${limit}`);
  }

  // Commentaires
  async getComments(limit = 100) {
    return this.request(`/responses/comments?limit=${limit}`);
  }

  // Statistiques
  async getStats() {
    return this.request('/responses/stats');
  }

  // Pages Facebook
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
}

export const api = new ApiService();
export default api;