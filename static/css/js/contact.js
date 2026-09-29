/**
 * BETA-Résilience - JavaScript pour le formulaire de contact
 */

document.addEventListener('DOMContentLoaded', function() {
    
    const contactForm = document.getElementById('contactForm');
    if (!contactForm) return;
    
    // --- Validation en temps réel ---
    const fields = contactForm.querySelectorAll('input, textarea, select');
    fields.forEach(function(field) {
        field.addEventListener('blur', function() {
            validateField(this);
        });
        field.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateField(this);
            }
        });
    });
    
    function validateField(field) {
        const errorEl = field.parentElement.querySelector('.invalid-feedback');
        if (!errorEl) return;
        
        if (field.hasAttribute('required') && !field.value.trim()) {
            field.classList.add('is-invalid');
            field.classList.remove('is-valid');
            errorEl.textContent = 'Ce champ est obligatoire.';
            return false;
        }
        
        if (field.type === 'email' && field.value.trim()) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(field.value.trim())) {
                field.classList.add('is-invalid');
                field.classList.remove('is-valid');
                errorEl.textContent = 'Veuillez saisir une adresse email valide.';
                return false;
            }
        }
        
        if (field.type === 'tel' && field.value.trim()) {
            const phoneRegex = /^[\d\s+()-]{6,15}$/;
            if (!phoneRegex.test(field.value.trim())) {
                field.classList.add('is-invalid');
                field.classList.remove('is-valid');
                errorEl.textContent = 'Veuillez saisir un numéro de téléphone valide.';
                return false;
            }
        }
        
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        return true;
    }
    
    // --- Submit avec validation complète ---
    contactForm.addEventListener('submit', function(e) {
        let isValid = true;
        fields.forEach(function(field) {
            if (!validateField(field)) {
                isValid = false;
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            // Scroll vers le premier champ invalide
            const firstInvalid = contactForm.querySelector('.is-invalid');
            if (firstInvalid) {
                firstInvalid.focus();
            }
        }
    });
    
    // --- Indicateur de saisie ---
    const messageField = contactForm.querySelector('textarea[name="message"]');
    if (messageField) {
        const counter = document.createElement('small');
        counter.className = 'text-muted float-end';
        counter.style.fontSize = '12px';
        messageField.parentElement.appendChild(counter);
        
        const maxLength = messageField.getAttribute('maxlength') || 1000;
        
        messageField.addEventListener('input', function() {
            const remaining = maxLength - this.value.length;
            counter.textContent = `${remaining} caractères restants`;
            
            if (remaining < 50) {
                counter.style.color = '#dc3545';
            } else {
                counter.style.color = '#6c757d';
            }
        });
        
        // Initialiser le compteur
        const initialRemaining = maxLength - (messageField.value.length || 0);
        counter.textContent = `${initialRemaining} caractères restants`;
    }
    
    // --- Protection anti-spam simple ---
    const honeypot = contactForm.querySelector('.honeypot');
    if (honeypot) {
        honeypot.style.display = 'none';
        honeypot.setAttribute('aria-hidden', 'true');
    }
});