import os
from datetime import timedelta

class Config:
    """Configuration de base de l'application"""
    
    # Configuration Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'votre_cle_secrete_ici_changez_la_en_production'
    
    # Configuration base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ste_releve.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration uploads
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    
    # Configuration session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    
    # Configuration pagination
    ITEMS_PER_PAGE = 20
    
    # Configuration graphiques
    GRAPH_DEFAULT_DAYS = 30
    GRAPH_MAX_DAYS = 365

class DevelopmentConfig(Config):
    """Configuration pour le développement"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuration pour la production"""
    DEBUG = False
    TESTING = False
    
    # En production, utilisez une vraie base de données
    # SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/ste_releve'

class TestingConfig(Config):
    """Configuration pour les tests"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration par défaut selon l'environnement
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 