#!/bin/bash
# Installation des dépendances
pip install -r requirements.txt

# Application des migrations directement sur Neon pendant le build Vercel
python manage.py migrate --noinput

# Collecte des fichiers statiques
python manage.py collectstatic --noinput
