import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_responses: 0,
    active_responses: 0,
    total_messages: 0,
    total_comments: 0,
    automated_messages: 0,
    automated_comments: 0
  });
  const [messages, setMessages] = useState([]);
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsData, messagesData, commentsData] = await Promise.all([
        api.getStats(),
        api.getMessages(10),
        api.getComments(10)
      ]);

      setStats(statsData);
      setMessages(messagesData);
      setComments(commentsData);
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-xl">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Tableau de bord</h1>

      {/* Statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm font-medium">Réponses automatiques</h3>
          <p className="text-3xl font-bold mt-2">{stats.active_responses}/{stats.total_responses}</p>
          <p className="text-sm text-gray-600 mt-1">Actives / Total</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm font-medium">Messages traités</h3>
          <p className="text-3xl font-bold mt-2">{stats.automated_messages}</p>
          <p className="text-sm text-gray-600 mt-1">Sur {stats.total_messages} total</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm font-medium">Commentaires traités</h3>
          <p className="text-3xl font-bold mt-2">{stats.automated_comments}</p>
          <p className="text-sm text-gray-600 mt-1">Sur {stats.total_comments} total</p>
        </div>
      </div>

      {/* Messages récents */}
      <div className="bg-white rounded-lg shadow mb-8">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold">Messages récents</h2>
        </div>
        <div className="divide-y">
          {messages.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              Aucun message pour le moment
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className="p-6 hover:bg-gray-50">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-medium">{msg.sender_name}</span>
                      {msg.is_automated && (
                        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                          Auto
                        </span>
                      )}
                    </div>
                    <p className="text-gray-700 mb-2">{msg.message_text}</p>
                    {msg.response_sent && (
                      <div className="bg-blue-50 p-3 rounded mt-2">
                        <p className="text-sm text-blue-900">
                          <strong>Réponse:</strong> {msg.response_sent}
                        </p>
                      </div>
                    )}
                  </div>
                  <div className="text-sm text-gray-500">
                    {new Date(msg.timestamp).toLocaleString('fr-FR')}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Commentaires récents */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold">Commentaires récents</h2>
        </div>
        <div className="divide-y">
          {comments.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              Aucun commentaire pour le moment
            </div>
          ) : (
            comments.map((comment) => (
              <div key={comment.id} className="p-6 hover:bg-gray-50">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-medium">{comment.user_name}</span>
                      {comment.is_automated && (
                        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                          Auto
                        </span>
                      )}
                    </div>
                    <p className="text-gray-700 mb-2">{comment.comment_text}</p>
                    {comment.response_sent && (
                      <div className="bg-blue-50 p-3 rounded mt-2">
                        <p className="text-sm text-blue-900">
                          <strong>Réponse:</strong> {comment.response_sent}
                        </p>
                      </div>
                    )}
                  </div>
                  <div className="text-sm text-gray-500">
                    {new Date(comment.timestamp).toLocaleString('fr-FR')}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;