import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

const Settings = () => {
  const [responses, setResponses] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    trigger_keyword: '',
    response_text: '',
    response_type: 'both',
    priority: 0,
    is_active: true
  });

  useEffect(() => {
    fetchResponses();
  }, []);

  const fetchResponses = async () => {
    try {
      const data = await api.getResponses();
      setResponses(data);
    } catch (error) {
      console.error('Erreur lors du chargement des réponses:', error);
    }
  };

  const handleInputChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setFormData({
      ...formData,
      [e.target.name]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      if (editingId) {
        await api.updateResponse(editingId, formData);
        alert('Réponse mise à jour avec succès!');
      } else {
        await api.createResponse(formData);
        alert('Réponse créée avec succès!');
      }

      resetForm();
      fetchResponses();
    } catch (error) {
      alert('Erreur lors de l\'enregistrement');
      console.error(error);
    }
  };

  const editResponse = (response) => {
    setFormData({
      trigger_keyword: response.trigger_keyword,
      response_text: response.response_text,
      response_type: response.response_type,
      priority: response.priority,
      is_active: response.is_active
    });
    setEditingId(response.id);
    setShowForm(true);
  };

  const deleteResponse = async (id) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette réponse?')) {
      try {
        await api.deleteResponse(id);
        fetchResponses();
      } catch (error) {
        console.error('Erreur lors de la suppression:', error);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      trigger_keyword: '',
      response_text: '',
      response_type: 'both',
      priority: 0,
      is_active: true
    });
    setEditingId(null);
    setShowForm(false);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Réponses automatiques</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
        >
          {showForm ? 'Annuler' : '+ Nouvelle réponse'}
        </button>
      </div>

      {/* Formulaire */}
      {showForm && (
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <h2 className="text-xl font-semibold mb-4">
            {editingId ? 'Modifier la réponse' : 'Créer une nouvelle réponse'}
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Mots-clés déclencheurs *
              </label>
              <input
                type="text"
                name="trigger_keyword"
                value={formData.trigger_keyword}
                onChange={handleInputChange}
                className="w-full p-2 border rounded"
                placeholder="ex: prix, tarif, horaire (séparés par des virgules)"
                required
              />
              <p className="text-sm text-gray-500 mt-1">
                Séparez plusieurs mots-clés par des virgules
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Texte de la réponse *
              </label>
              <textarea
                name="response_text"
                value={formData.response_text}
                onChange={handleInputChange}
                className="w-full p-2 border rounded"
                rows="4"
                placeholder="Le texte qui sera envoyé automatiquement"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Type de réponse
              </label>
              <select
                name="response_type"
                value={formData.response_type}
                onChange={handleInputChange}
                className="w-full p-2 border rounded"
              >
                <option value="both">Messages et Commentaires</option>
                <option value="message">Messages privés uniquement</option>
                <option value="comment">Commentaires uniquement</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Priorité
              </label>
              <input
                type="number"
                name="priority"
                value={formData.priority}
                onChange={handleInputChange}
                className="w-full p-2 border rounded"
                placeholder="0"
              />
              <p className="text-sm text-gray-500 mt-1">
                Les réponses avec une priorité plus élevée seront vérifiées en premier
              </p>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                name="is_active"
                checked={formData.is_active}
                onChange={handleInputChange}
                className="mr-2"
              />
              <label className="text-sm font-medium">
                Active
              </label>
            </div>

            <div className="flex gap-4">
              <button
                type="submit"
                className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
              >
                {editingId ? 'Mettre à jour' : 'Créer'}
              </button>
              <button
                type="button"
                onClick={resetForm}
                className="bg-gray-300 text-gray-700 px-6 py-2 rounded hover:bg-gray-400"
              >
                Annuler
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Liste des réponses */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold">Réponses configurées</h2>
        </div>

        {responses.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            Aucune réponse configurée. Créez votre première réponse automatique!
          </div>
        ) : (
          <div className="divide-y">
            {responses.map((response) => (
              <div key={response.id} className="p-6 hover:bg-gray-50">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-medium">
                        {response.trigger_keyword}
                      </h3>
                      <span className={`px-2 py-1 text-xs rounded ${
                        response.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {response.is_active ? 'Active' : 'Inactive'}
                      </span>
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                        {response.response_type === 'both' ? 'Messages & Commentaires' :
                         response.response_type === 'message' ? 'Messages' : 'Commentaires'}
                      </span>
                      {response.priority > 0 && (
                        <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">
                          Priorité: {response.priority}
                        </span>
                      )}
                    </div>
                    <p className="text-gray-700 whitespace-pre-wrap">
                      {response.response_text}
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                      Créée le {new Date(response.created_at).toLocaleDateString('fr-FR')}
                    </p>
                  </div>

                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => editResponse(response)}
                      className="text-blue-600 hover:text-blue-800 px-3 py-1 rounded border border-blue-600 hover:bg-blue-50"
                    >
                      Modifier
                    </button>
                    <button
                      onClick={() => deleteResponse(response.id)}
                      className="text-red-600 hover:text-red-800 px-3 py-1 rounded border border-red-600 hover:bg-red-50"
                    >
                      Supprimer
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Aide */}
      <div className="mt-8 bg-yellow-50 p-6 rounded-lg">
        <h3 className="font-semibold mb-2">💡 Conseils</h3>
        <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
          <li>Utilisez plusieurs mots-clés séparés par des virgules pour une même réponse</li>
          <li>Les réponses avec une priorité plus élevée sont vérifiées en premier</li>
          <li>Testez vos réponses sur votre page avant de les activer</li>
          <li>Vous pouvez désactiver temporairement une réponse sans la supprimer</li>
        </ul>
      </div>
    </div>
  );
};

export default Settings;