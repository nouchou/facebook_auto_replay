import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';

export default function ResponseModal({ isOpen, onClose, onSubmit, editingResponse }) {
  const [formData, setFormData] = useState({
    trigger_keyword: '',
    response_text: '',
    response_type: 'both',
    priority: 0,
    is_active: true,
  });

  useEffect(() => {
    if (editingResponse) {
      setFormData(editingResponse);
    } else {
      setFormData({
        trigger_keyword: '',
        response_text: '',
        response_type: 'both',
        priority: 0,
        is_active: true,
      });
    }
  }, [editingResponse, isOpen]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto animate-slide-up">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 sticky top-0 bg-white">
          <h3 className="text-xl font-semibold text-gray-900">
            {editingResponse ? 'Modifier la réponse' : 'Nouvelle réponse automatique'}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6">
          <div className="space-y-5">
            {/* Mots-clés */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Mots-clés déclencheurs <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="trigger_keyword"
                value={formData.trigger_keyword}
                onChange={handleChange}
                className="input-field"
                placeholder="bonjour, salut, hey"
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                Séparez plusieurs mots-clés par des virgules. Le système recherchera ces mots dans les messages.
              </p>
            </div>

            {/* Texte de réponse */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Texte de la réponse <span className="text-red-500">*</span>
              </label>
              <textarea
                name="response_text"
                value={formData.response_text}
                onChange={handleChange}
                className="input-field"
                rows="5"
                placeholder="Bonjour ! Merci pour votre message. Comment puis-je vous aider ?"
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                {formData.response_text.length} caractères
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Type de réponse */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Type de réponse
                </label>
                <select
                  name="response_type"
                  value={formData.response_type}
                  onChange={handleChange}
                  className="input-field"
                >
                  <option value="both">Messages et Commentaires</option>
                  <option value="message">Messages uniquement</option>
                  <option value="comment">Commentaires uniquement</option>
                </select>
              </div>

              {/* Priorité */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Priorité (0-10)
                </label>
                <input
                  type="number"
                  name="priority"
                  value={formData.priority}
                  onChange={handleChange}
                  className="input-field"
                  min="0"
                  max="10"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Plus la priorité est élevée, plus elle sera traitée en premier
                </p>
              </div>
            </div>

            {/* Statut actif */}
            <div className="flex items-center">
              <input
                type="checkbox"
                name="is_active"
                id="is_active"
                checked={formData.is_active}
                onChange={handleChange}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="is_active" className="ml-2 text-sm font-medium text-gray-700">
                Activer cette réponse automatique
              </label>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-6 flex justify-end space-x-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary"
            >
              Annuler
            </button>
            <button
              type="submit"
              className="btn-primary"
            >
              {editingResponse ? 'Mettre à jour' : 'Créer'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}