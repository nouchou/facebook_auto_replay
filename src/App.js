import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import PageConnection from './pages/PageConnection';
import Settings from './pages/Settings';
import Login from './pages/Login';
import Navbar from './components/Navbar';
import { api } from './services/api';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');

    if (!token) {
      setLoading(false);
      return;
    }

    try {
      // Vérifier la validité du token
      const data = await api.verifyToken(token);
      
      if (data.valid) {
        setIsAuthenticated(true);
        setUser(savedUser || data.user);
        
        // Vérifier la connexion Facebook
        await checkConnection();
      } else {
        // Token invalide, déconnecter
        handleLogout();
      }
    } catch (error) {
      console.error('Erreur de vérification:', error);
      handleLogout();
    } finally {
      setLoading(false);
    }
  };

  const checkConnection = async () => {
    try {
      const pages = await api.getPages();
      setIsConnected(pages.length > 0 && pages.some(p => p.is_active));
    } catch (error) {
      console.error('Erreur de connexion:', error);
      setIsConnected(false);
    }
  };

  const handleLogin = (data) => {
    setIsAuthenticated(true);
    setUser(data.user);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    setUser(null);
    setIsConnected(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {isAuthenticated && isConnected && <Navbar user={user} onLogout={handleLogout} />}
        
        <Routes>
          {/* Route de connexion */}
          <Route 
            path="/login" 
            element={
              isAuthenticated ? (
                <Navigate to="/" replace />
              ) : (
                <Login onLogin={handleLogin} />
              )
            } 
          />

          {/* Route de connexion Facebook */}
          <Route 
            path="/connect" 
            element={
              !isAuthenticated ? (
                <Navigate to="/login" replace />
              ) : (
                <PageConnection onConnect={() => {
                  setIsConnected(true);
                }} />
              )
            } 
          />

          {/* Route Dashboard */}
          <Route 
            path="/" 
            element={
              !isAuthenticated ? (
                <Navigate to="/login" replace />
              ) : !isConnected ? (
                <Navigate to="/connect" replace />
              ) : (
                <Dashboard />
              )
            } 
          />

          {/* Route Settings */}
          <Route 
            path="/settings" 
            element={
              !isAuthenticated ? (
                <Navigate to="/login" replace />
              ) : !isConnected ? (
                <Navigate to="/connect" replace />
              ) : (
                <Settings />
              )
            } 
          />

          {/* Route par défaut */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;