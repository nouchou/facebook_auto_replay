import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_ENV') == 'development'
    
    # Database - CORRIGÉ pour PostgreSQL sur Render
    database_url = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    # Render utilise postgres:// mais SQLAlchemy nécessite postgresql://
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Facebook
    FACEBOOK_APP_ID = os.getenv('2404163833372728')
    FACEBOOK_APP_SECRET = os.getenv('ce10504723897f50831d9eb1cc6c2199')
    FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv('EAAiKkwNFIDgBPwhjq5fZAAD8dZBkhbn02EqXXo7cSbVmW8NeQD2MzBLYHFwqpCGnTaFJ0mKI1bLZB0b0DOboS0YDBiD6kd5zoCvo2iQyPU9YsIqGcAaUJic4YDpufdVFcGdOo3ZC77Jr28MtU6z7Ic6TE7uivXXZA4Vj23clfV8VBt2bPNsLkokrrhDCYez6soZAZAYyneBDgZDZD')
    FACEBOOK_VERIFY_TOKEN = os.getenv('my_verify_token_123', 'my_verify_token_123')
    FACEBOOK_GRAPH_VERSION = 'v24.0'
    
    # CORS - Ajoutez votre domaine Render
    CORS_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:5173',
        'http://localhost:5174',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:5174', 
        'https://facebook-auto-replay.onrender.com'
    ]