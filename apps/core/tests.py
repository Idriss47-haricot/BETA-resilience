"""
Tests automatisés pour BETA-Résilience
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.core.models import Page, SiteConfiguration
from apps.membres.models import Membre, DemandeAdhesion
from apps.projets.models import Projet, CategorieProjet
from apps.actualites.models import Article, CategorieActualite
from apps.services.models import Service
from apps.partenaires.models import Partenaire
from apps.documents.models import Document, CategorieDocument
from apps.contacts.models import MessageContact


class CoreTests(TestCase):
    """Tests pour l'application Core"""
    
    def setUp(self):
        """Configuration des tests"""
        self.client = Client()
        
        # Créer une configuration du site
        self.site_config = SiteConfiguration.objects.create(
            site_name='BETA-Résilience',
            site_tagline='Test Tagline',
            email='test@beta-resilience.org'
        )
        
        # Créer une page statique
        self.page = Page.objects.create(
            title='Test Page',
            slug='test-page',
            content='Test content',
            is_published=True
        )
    
    def test_homepage(self):
        """Test de la page d'accueil"""
        response = self.client.get(reverse('core:accueil'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/accueil.html')
        self.assertContains(response, 'BETA-Résilience')
    
    def test_page_detail(self):
        """Test de la page détail"""
        response = self.client.get(reverse('core:page_detail', kwargs={'slug': 'test-page'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Page')
        self.assertContains(response, 'Test content')
    
    def test_about_page(self):
        """Test de la page À Propos"""
        response = self.client.get(reverse('core:a_propos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/a_propos.html')
    
    def test_404_page(self):
        """Test de la page 404"""
        response = self.client.get('/page-inexistante/')
        self.assertEqual(response.status_code, 404)


class MembresTests(TestCase):
    """Tests pour l'application Membres"""
    
    def setUp(self):
        self.client = Client()
        
        # Créer un membre
        self.membre = Membre.objects.create(
            nom='Voundi',
            prenom='Eric',
            email='eric.voundi@test.com',
            biographie='Test biographie',
            est_actif=True,
            est_membre_bureau=True
        )
    
    def test_equipe_page(self):
        """Test de la page équipe"""
        response = self.client.get(reverse('membres:equipe'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Eric Voundi')
    
    def test_membre_detail(self):
        """Test du détail d'un membre"""
        response = self.client.get(reverse('membres:detail', kwargs={'slug': self.membre.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test biographie')
    
    def test_adhesion_form(self):
        """Test du formulaire d'adhésion"""
        response = self.client.get(reverse('membres:adhesion'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'membres/adhesion.html')
        
        # Test de soumission
        data = {
            'nom': 'Test',
            'prenom': 'User',
            'email': 'user@test.com',
            'telephone': '691234567',
            'motivation': 'Je veux adhérer pour tester',
            'competences': 'Test compétences',
        }
        response = self.client.post(reverse('membres:adhesion'), data)
        self.assertEqual(response.status_code, 302)  # Redirection après succès


class ProjetsTests(TestCase):
    """Tests pour l'application Projets"""
    
    def setUp(self):
        self.client = Client()
        
        # Créer une catégorie
        self.categorie = CategorieProjet.objects.create(
            nom='Environnement',
            slug='environnement'
        )
        
        # Créer un projet
        self.projet = Projet.objects.create(
            titre='Projet Test',
            slug='projet-test',
            description_courte='Description test',
            date_debut='2024-01-01',
            statut='en_cours',
            est_publie=True
        )
        self.projet.categories.add(self.categorie)
    
    def test_projets_list(self):
        """Test de la liste des projets"""
        response = self.client.get(reverse('projets:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Projet Test')
    
    def test_projet_detail(self):
        """Test du détail d'un projet"""
        response = self.client.get(reverse('projets:detail', kwargs={'slug': 'projet-test'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Description test')
    
    def test_projet_filters(self):
        """Test des filtres de projets"""
        response = self.client.get(reverse('projets:list') + '?statut=en_cours')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('projets:list') + '?categorie=environnement')
        self.assertEqual(response.status_code, 200)


class ActualitesTests(TestCase):
    """Tests pour l'application Actualités"""
    
    def setUp(self):
        self.client = Client()
        
        # Créer une catégorie
        self.categorie = CategorieActualite.objects.create(
            nom='Actualité',
            slug='actualite'
        )
        
        # Créer un article
        self.article = Article.objects.create(
            titre='Article Test',
            slug='article-test',
            contenu='<p>Contenu de test</p>',
            est_publie=True,
            statut='publie'
        )
        self.article.categories.add(self.categorie)
    
    def test_actualites_list(self):
        """Test de la liste des actualités"""
        response = self.client.get(reverse('actualites:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Article Test')
    
    def test_article_detail(self):
        """Test du détail d'un article"""
        response = self.client.get(reverse('actualites:detail', kwargs={'slug': 'article-test'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contenu de test')


class ContactsTests(TestCase):
    """Tests pour l'application Contacts"""
    
    def test_contact_form(self):
        """Test du formulaire de contact"""
        response = self.client.get(reverse('contacts:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contacts/contact.html')
        
        # Test de soumission
        data = {
            'nom': 'Test',
            'prenom': 'User',
            'email': 'user@test.com',
            'sujet': 'general',
            'message': 'Test message',
            'honeypot': '',
        }
        response = self.client.post(reverse('contacts:contact'), data)
        # Vérifier que le message a été sauvegardé
        self.assertEqual(MessageContact.objects.count(), 1)


class DocumentsTests(TestCase):
    """Tests pour l'application Documents"""
    
    def setUp(self):
        self.client = Client()
        
        self.categorie = CategorieDocument.objects.create(
            nom='Rapports',
            slug='rapports'
        )
        
        # Créer un document (sans fichier pour le test)
        self.document = Document.objects.create(
            titre='Document Test',
            slug='document-test',
            categorie=self.categorie,
            est_publie=True
        )
    
    def test_documents_list(self):
        """Test de la liste des documents"""
        response = self.client.get(reverse('documents:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Document Test')