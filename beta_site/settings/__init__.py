"""
Configuration Django pour BETA-Résilience
"""
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Déterminer l'environnement
ENVIRONMENT = os.getenv('DJANGO_ENV', 'development')

if ENVIRONMENT == 'production':
    from .production import *
else:
    from .development import *