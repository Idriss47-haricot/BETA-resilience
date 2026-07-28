@echo off
echo 🚀 Activation de l'environnement virtuel...
call env\Scripts\activate
echo ✅ Environnement activé !
echo 📁 Dossier : %CD%
echo 📦 Paquets installés :
pip list --format=columns | findstr django
cmd /k