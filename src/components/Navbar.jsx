import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Bot, Home, Settings as SettingsIcon, LogOut, User, ChevronDown } from 'lucide-react';

export default function Navbar({ user, onLogout }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const isActive = (path) => {
    return location.pathname === path;
  };

  const handleLogout = () => {
    if (window.confirm('Êtes-vous sûr de vouloir vous déconnecter ?')) {
      onLogout();
      navigate('/login');
    }
  };

  return (
    <nav className="bg-white shadow-sm border-b sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-3">
              <Bot className="w-8 h-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-900">
                AutoResponse FB
              </span>
            </Link>

            {/* Navigation */}
            <div className="hidden sm:ml-10 sm:flex sm:space-x-8">
              <Link
                to="/"
                className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors ${
                  isActive('/')
                    ? 'border-blue-600 text-gray-900'
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                }`}
              >
                <Home className="w-4 h-4 mr-2" />
                Dashboard
              </Link>

              <Link
                to="/settings"
                className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors ${
                  isActive('/settings')
                    ? 'border-blue-600 text-gray-900'
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                }`}
              >
                <SettingsIcon className="w-4 h-4 mr-2" />
                Paramètres
              </Link>
            </div>
          </div>

          {/* Desktop - Right side */}
          <div className="hidden sm:flex items-center space-x-4">
            {/* Indicateur de statut */}
            <div className="flex items-center space-x-2 px-3 py-1 bg-green-50 rounded-full">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-green-700 font-medium">Connecté</span>
            </div>

            {/* Bouton utilisateur avec dropdown */}
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-2 px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
              >
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                  <User className="w-5 h-5 text-white" />
                </div>
                <span className="text-sm font-medium text-gray-700">
                  {user || 'Admin'}
                </span>
                <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${showUserMenu ? 'rotate-180' : ''}`} />
              </button>

              {/* Dropdown menu */}
              {showUserMenu && (
                <>
                  <div 
                    className="fixed inset-0 z-10"
                    onClick={() => setShowUserMenu(false)}
                  />
                  
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-xl py-1 z-20 border border-gray-200">
                    <div className="px-4 py-3 border-b border-gray-100">
                      <p className="text-sm font-semibold text-gray-900">{user || 'Admin'}</p>
                      <p className="text-xs text-gray-500 mt-0.5">Administrateur</p>
                    </div>
                    
                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-3 text-sm text-red-600 hover:bg-red-50 flex items-center space-x-3 font-medium transition-colors"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Se déconnecter</span>
                    </button>
                  </div>
                </>
              )}
            </div>

            {/* OU Bouton de déconnexion direct (alternative) */}
            {/* Décommentez cette section si vous préférez un bouton direct */}
            {/*
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors border border-red-200"
            >
              <LogOut className="w-4 h-4" />
              <span className="text-sm font-medium">Déconnexion</span>
            </button>
            */}
          </div>

          {/* Mobile - Right side */}
          <div className="flex sm:hidden items-center space-x-2">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            </div>
            
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="p-2 rounded-lg hover:bg-gray-100"
            >
              <User className="w-6 h-6 text-gray-600" />
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      <div className="sm:hidden border-t bg-white">
        <div className="pt-2 pb-3 space-y-1">
          <Link
            to="/"
            className={`block pl-3 pr-4 py-3 border-l-4 text-base font-medium ${
              isActive('/')
                ? 'bg-blue-50 border-blue-600 text-blue-700'
                : 'border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800'
            }`}
          >
            <div className="flex items-center">
              <Home className="w-5 h-5 mr-3" />
              Dashboard
            </div>
          </Link>
          
          <Link
            to="/settings"
            className={`block pl-3 pr-4 py-3 border-l-4 text-base font-medium ${
              isActive('/settings')
                ? 'bg-blue-50 border-blue-600 text-blue-700'
                : 'border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800'
            }`}
          >
            <div className="flex items-center">
              <SettingsIcon className="w-5 h-5 mr-3" />
              Paramètres
            </div>
          </Link>

          {/* User info mobile */}
          <div className="border-t border-gray-200 pt-3 mt-3">
            <div className="px-4 py-2 bg-gray-50">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                  <User className="w-6 h-6 text-white" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-900">{user || 'Admin'}</p>
                  <p className="text-xs text-gray-500">Administrateur</p>
                </div>
              </div>
            </div>

            <button
              onClick={handleLogout}
              className="w-full text-left block pl-3 pr-4 py-3 border-l-4 border-transparent text-red-600 hover:bg-red-50 hover:border-red-300 text-base font-medium mt-1"
            >
              <div className="flex items-center">
                <LogOut className="w-5 h-5 mr-3" />
                <span>Se déconnecter</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}