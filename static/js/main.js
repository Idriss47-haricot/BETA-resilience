/**
 * main.js - Scripts principaux du projet BETA-Résilience
 */

document.addEventListener('DOMContentLoaded', function () {
    console.log('Fichier main.js chargé avec succès.');

    // 1. Masquage automatique des messages d'alerte Django après 5 secondes
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } else {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 500);
            }
        }, 5000);
    });

    // 2. Gestion dynamique du champ "Autre type" dans les formulaires de demande
    const entiteSelect = document.getElementById('id_entite');
    const typeSelect = document.getElementById('id_type_demande');
    const autreTypeContainer = document.getElementById('div_id_autre_type') || document.querySelector('.field-autre_type');

    if (autreTypeContainer && typeSelect) {
        function toggleAutreType() {
            if (typeSelect.value === 'autre' || typeSelect.value === 'Other') {
                autreTypeContainer.style.display = 'block';
            } else {
                autreTypeContainer.style.display = 'none';
            }
        }

        // Vérification au chargement et au changement
        toggleAutreType();
        typeSelect.addEventListener('change', toggleAutreType);
    }

    // 3. Validation de la taille du fichier joint côté client (max 5 Mo)
    const fichierInput = document.getElementById('id_fichier');
    if (fichierInput) {
        fichierInput.addEventListener('change', function () {
            const file = this.files[0];
            if (file) {
                const maxSize = 5 * 1024 * 1024; // 5 Mo en octets
                if (file.size > maxSize) {
                    alert('Le fichier sélectionné dépasse la taille maximale autorisée de 5 Mo.');
                    this.value = ''; // Réinitialiser le champ
                }
            }
        });
    }
});
