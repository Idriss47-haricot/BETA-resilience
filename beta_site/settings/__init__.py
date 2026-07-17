"""
Configuration Django pour BETA-Résilience
"""
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Déterminer l'environnement
ENVIRONMENT = os.getenv('DJANGO_ENV', 'development')

# Vercel définit automatiquement VERCEL=1 sur toutes ses machines —
# on force donc la production dès qu'on détecte Vercel, peu importe DJANGO_ENV
if os.getenv('VERCEL') == '1':
    ENVIRONMENT = 'production'

if ENVIRONMENT == 'production':
    from .production import *
else:
    from .development import *
