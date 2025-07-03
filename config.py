'''
Configuration management for Flask application.
'''
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

class Config:
    """Base configuration class."""
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Development configuration."""
    ENVIRONMENT = 'dev'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')  # SQLite in dev

class ProductionConfig(Config):
    """Production configuration."""
    ENVIRONMENT = 'prod'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')  # PostgreSQL in prod

# Select config based on ENVIRONMENT
if os.getenv('ENVIRONMENT') == 'prod':
    config = ProductionConfig()
else:
    config = DevelopmentConfig()
