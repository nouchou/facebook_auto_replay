import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

const PageConnection = ({ onConnect }) => {
  const [pages, setPages] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    page_id: '',
    page_name: '',
    access_token: ''
  });
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  useEffect(() => {
    fetchPages();
  }, []);

  const fetchPages = async () => {
    try {
      const data = await api.getPages();
      setPages(data);
    } catch (error) {
      console.error('Erreur lors du chargement des pages:', error);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const testConnection = async () => {
    if (!formData.access_token) {
      alert('Veuillez entrer un token d\'accès');
      return;
    }

    setTesting(true);
    setTestResult(null);

    try {
      const data = await api.testConnection(formData.access_token);

      setTestResult({
        success: true,
        message: 'Connexion réussie!',
        data: data.page_info
      });

      // Pré-remplir les infos si disponibles
      if (data.page_info) {
        setFormData({
          ...formData,
          page_id: data.page_info.id || formData.page_id,
          page_name: data.page_info.name || formData.page_name
        });
      }
    } catch (error) {
      setTestResult({
        success: false,
        message: 'Échec de la connexion. Vérifiez votre token.'
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await api.connectPage(formData);
      alert('Page connectée avec succès!');
      setShowForm(false);
      setFormData({ page_id: '', page_name: '', access_token: '' });
      setTestResult(null);
      fetchPages();
      if (onConnect) onConnect();
    } catch (error) {
      alert('Erreur lors de la connexion de la page');
      console.error(error);
    }
  };

  const togglePage = async (pageId) => {
    try {
      await api.togglePage(pageId);
      fetchPages();
    } catch (error) {
      console.error('Erreur lors de la modification du statut:', error);
    }
  };

  const deletePage = async (pageId) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette page?')) {
      try {
        await api.disconnectPage(pageId);
        fetchPages();
      } catch (error) {
        console.error('Erreur lors de la suppression:', error);
      }
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Pages Facebook</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
        >
          {showForm ? 'Annuler' : '+ Connecter une page'}
        </button>
      </div>

      {/* Formulaire de connexion */}
      {showForm && (
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <h2 className="text-xl font-semibold mb-4">Connecter une nouvelle page</h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Token d'accès *
              </label>
              <input
                type="text"
                name="access_token"
                value={formData.access_token}
                onChange={handleInputChange}
                className="w-full p-2 border rounded"
                placeholder="Votre token d'accès Facebook"
                required
              />
              <button
                type="button"
                onClick={testConnection}
                disabled={testing}
                className="mt-2 text-sm text-blue-600 hover:underline"
              >
                {testing ? 'Test en cours...' : 'Tester la connexion'}
              </button>
            </div>

            {testResult && (
              <div className={`p-4 rounded ${testResult.success ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
                {testResult.message}
                {testResult.data && (
                  <div className="mt-2 text-sm">
                    <strong>ID:</strong> {testResult.data.id}<br />
                    <strong>Nom:</strong> {testResult.data.name}
                  </div>
                )}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium mb-2">
                ID de la page *
              </label>
              <input
                type="text"
                name="page_id"
                value={formData.page_id}
                onChange={handleInputChange}
                className="w-full p-2 border rounded"
                placeholder="ID de votre page Facebook"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Nom de la page
              </label>
              <input
                type="text"
                name="page_name"
                value={formData.page_name}
                onChange={handleInputChange}
                className="w-full p-2 border rounded"
                placeholder="Nom de votre page"
              />
            </div>

            <div className="flex gap-4">
              <button
                type="submit"
                className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
              >
                Connecter
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowForm(false);
                  setFormData({ page_id: '', page_name: '', access_token: '' });
                  setTestResult(null);
                }}
                className="bg-gray-300 text-gray-700 px-6 py-2 rounded hover:bg-gray-400"
              >
                Annuler
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Liste des pages */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold">Pages connectées</h2>
        </div>

        {pages.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            Aucune page connectée. Cliquez sur "Connecter une page" pour commencer.
          </div>
        ) : (
          <div className="divide-y">
            {pages.map((page) => (
              <div key={page.id} className="p-6 flex justify-between items-center">
                <div>
                  <h3 className="font-medium text-lg">{page.page_name}</h3>
                  <p className="text-sm text-gray-500">ID: {page.page_id}</p>
                  <p className="text-sm text-gray-500">
                    Connectée le {new Date(page.created_at).toLocaleDateString('fr-FR')}
                  </p>
                </div>

                <div className="flex items-center gap-4">
                  <button
                    onClick={() => togglePage(page.id)}
                    className={`px-4 py-2 rounded ${
                      page.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {page.is_active ? 'Active' : 'Inactive'}
                  </button>

                  <button
                    onClick={() => deletePage(page.id)}
                    className="text-red-600 hover:text-red-800"
                  >
                    Supprimer
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="mt-8 bg-blue-50 p-6 rounded-lg">
        <h3 className="font-semibold mb-2">Comment obtenir votre token d'accès?</h3>
        <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700">
          <li>Allez sur <a href="https://developers.facebook.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Facebook Developers</a></li>
          <li>Créez une application et configurez-la pour votre page</li>
          <li>Dans les outils, générez un token d'accès pour votre page</li>
          <li>Copiez le token et collez-le ci-dessus</li>
        </ol>
      </div>
    </div>
  );
};

export default PageConnection;