/**
 * BETA-Résilience - JavaScript Principal
 * Fonctionnalités interactives du site
 */

// Attendre le chargement complet du DOM
document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. NAVBAR SCROLL EFFECT ---
    const navbar = document.getElementById('mainNav');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 100) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
    }
    
    // --- 2. SCROLL TO TOP BUTTON ---
    const scrollBtn = document.getElementById('scrollTopBtn');
    if (scrollBtn) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                scrollBtn.style.display = 'block';
            } else {
                scrollBtn.style.display = 'none';
            }
        });
        
        scrollBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // --- 3. FORMULAIRE : Validation côté client ---
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // --- 4. ANIMATIONS AU SCROLL (AOS) ---
    // AOS est déjà initialisé dans base.html
    
    // --- 5. TOOLTIPS ---
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // --- 6. MENU MOBILE : Fermer automatiquement ---
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const navbarCollapse = document.getElementById('mainNavbar');
    if (navbarCollapse) {
        navLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                if (bsCollapse) {
                    bsCollapse.hide();
                }
            });
        });
    }
    
    // --- 7. COMPTEUR DE TÉLÉCHARGEMENTS (AJAX) ---
    const downloadLinks = document.querySelectorAll('.download-link');
    downloadLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            // Le compteur est géré côté serveur
            // On peut ajouter un indicateur visuel
            const countEl = this.querySelector('.download-count');
            if (countEl) {
                const current = parseInt(countEl.textContent) || 0;
                countEl.textContent = current + 1;
            }
        });
    });
    
    // --- 8. FILTRAGE DYNAMIQUE DES PROJETS ---
    const filterSelects = document.querySelectorAll('.filter-select');
    filterSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            this.closest('form').submit();
        });
    });
    
    // --- 9. COPIER LE LIEN ---
    const copyButtons = document.querySelectorAll('.copy-link-btn');
    copyButtons.forEach(function(btn) {
        btn.addEventListener('click', function() {
            const url = this.getAttribute('data-url');
            if (url) {
                navigator.clipboard.writeText(url).then(function() {
                    // Feedback visuel
                    btn.innerHTML = '<i class="fas fa-check"></i> Copié !';
                    setTimeout(function() {
                        btn.innerHTML = '<i class="fas fa-copy"></i>';
                    }, 2000);
                });
            }
        });
    });
    
    // --- 10. SMOOTH SCROLL POUR ANCRES ---
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                const navbarHeight = document.getElementById('mainNav')?.offsetHeight || 80;
                const targetPosition = target.getBoundingClientRect().top + window.scrollY - navbarHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // --- 11. COMPTEUR STATISTIQUES (Animation) ---
    const statElements = document.querySelectorAll('.stat-number');
    statElements.forEach(function(el) {
        const target = parseInt(el.getAttribute('data-target')) || 0;
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;
        
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const timer = setInterval(function() {
                        current += step;
                        if (current >= target) {
                            el.textContent = target + '+';
                            clearInterval(timer);
                        } else {
                            el.textContent = Math.floor(current) + '+';
                        }
                    }, 16);
                    observer.unobserve(el);
                }
            });
        });
        observer.observe(el);
    });
    
    // --- 12. CONFIRMATION DE SUPPRESSION ---
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    deleteButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            if (!confirm('Êtes-vous sûr de vouloir supprimer cet élément ?')) {
                e.preventDefault();
            }
        });
    });
    
    // --- 13. GESTION DES MESSAGES FLASH ---
    const flashMessages = document.querySelectorAll('.alert-dismissible');
    flashMessages.forEach(function(msg) {
        setTimeout(function() {
            const closeBtn = msg.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            }
        }, 5000);
    });
    
    // --- 14. CHARGEMENT DES IMAGES LAZY ---
    if ('loading' in HTMLImageElement.prototype) {
        const images = document.querySelectorAll('img[loading="lazy"]');
        images.forEach(function(img) {
            img.src = img.dataset.src || img.src;
        });
    }
    
    // --- 15. DARK MODE TOGGLE (optionnel) ---
    // Cette fonction peut être activée si besoin
    function toggleDarkMode() {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDark);
    }
    
    // Vérifier la préférence stockée
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
    }
    
    // Exposer la fonction globalement
    window.toggleDarkMode = toggleDarkMode;
    
    console.log('🌿 BETA-Résilience - Site chargé avec succès !');
});