"""
Statistiques personnelles des membres
"""
from django.db.models import Count, Q
from django.utils import timezone
from apps.demandes.models import Demande
# from apps.evenements.models import InscriptionEvenement  # ← COMMENTE CETTE LIGNE
# from apps.forums.models import ForumMessage  # ← COMMENTE CETTE LIGNE


def get_stats_membre(user):
    """
    Récupérer toutes les statistiques d'un membre
    """
    stats = {
        'demandes': get_stats_demandes(user),
        # 'evenements': get_stats_evenements(user),  # ← COMMENTE
        # 'forums': get_stats_forums(user),  # ← COMMENTE
        'activite': get_stats_activite(user),
        'progression': get_stats_progression(user),
    }
    return stats


def get_stats_demandes(user):
    """
    Statistiques des demandes
    """
    demandes = Demande.objects.filter(email=user.email)
    
    return {
        'total': demandes.count(),
        'en_attente': demandes.filter(statut='en_attente').count(),
        'en_cours': demandes.filter(statut='en_cours').count(),
        'traitees': demandes.filter(statut='traite').count(),
        'rejetees': demandes.filter(statut='rejete').count(),
        'par_entite': demandes.values('entite').annotate(total=Count('id')),
        'evolution': get_evolution_demandes(demandes),
    }


# def get_stats_evenements(user):  # ← COMMENTE
#     """
#     Statistiques des événements
#     """
#     inscriptions = InscriptionEvenement.objects.filter(utilisateur=user)
#     
#     return {
#         'total': inscriptions.count(),
#         'confirmees': inscriptions.filter(statut='confirme').count(),
#         'liste_attente': inscriptions.filter(statut='liste_attente').count(),
#         'annulees': inscriptions.filter(statut='annule').count(),
#         'a_venir': inscriptions.filter(evenement__statut='a_venir').count(),
#         'termines': inscriptions.filter(evenement__statut='termine').count(),
#     }


# def get_stats_forums(user):  # ← COMMENTE
#     """
#     Statistiques des forums
#     """
#     from apps.forums.models import ForumSujet, ForumMessage
#     
#     sujets = ForumSujet.objects.filter(auteur=user)
#     messages = ForumMessage.objects.filter(auteur=user)
#     
#     return {
#         'sujets': sujets.count(),
#         'messages': messages.count(),
#         'dernier_message': messages.order_by('-date_creation').first(),
#     }


def get_stats_activite(user):
    """
    Statistiques d'activité
    """
    from django.contrib.auth.models import User
    
    # Dernière connexion
    derniere_connexion = user.last_login
    
    # Jours d'activité (simulé)
    jours_activite = 0
    
    return {
        'derniere_connexion': derniere_connexion,
        'jours_activite': jours_activite,
    }


def get_stats_progression(user):
    """
    Statistiques de progression (gamification)
    """
    points = 0
    badges = []
    
    # Compter les points
    demandes = Demande.objects.filter(email=user.email)
    points += demandes.count() * 10
    
    # from apps.forums.models import ForumMessage  # ← COMMENTE
    # messages = ForumMessage.objects.filter(auteur=user)  # ← COMMENTE
    # points += messages.count() * 2  # ← COMMENTE
    
    # inscriptions = InscriptionEvenement.objects.filter(utilisateur=user)  # ← COMMENTE
    # points += inscriptions.count() * 5  # ← COMMENTE
    
    # Badges
    if demandes.count() >= 1:
        badges.append({'nom': 'Première demande', 'icone': '🎯'})
    if demandes.count() >= 10:
        badges.append({'nom': '10 demandes', 'icone': '📝'})
    # if messages.count() >= 50:  # ← COMMENTE
    #     badges.append({'nom': '50 messages', 'icone': '🗣️'})
    
    # Niveau
    niveau = 'Nouveau membre'
    if points >= 500:
        niveau = 'Ambassadeur'
    elif points >= 200:
        niveau = 'Expert'
    elif points >= 100:
        niveau = 'Membre engagé'
    elif points >= 50:
        niveau = 'Membre actif'
    
    return {
        'points': points,
        'niveau': niveau,
        'badges': badges,
        'prochain_niveau': get_prochain_niveau(points),
    }


def get_evolution_demandes(demandes):
    """
    Évolution des demandes par mois
    """
    from django.db.models.functions import TruncMonth
    return demandes.annotate(
        mois=TruncMonth('date_soumission')
    ).values('mois').annotate(
        total=Count('id')
    ).order_by('mois')


def get_prochain_niveau(points):
    """
    Points nécessaires pour le prochain niveau
    """
    if points < 50:
        return {'nom': 'Membre actif', 'points_restants': 50 - points}
    elif points < 100:
        return {'nom': 'Membre engagé', 'points_restants': 100 - points}
    elif points < 200:
        return {'nom': 'Expert', 'points_restants': 200 - points}
    elif points < 500:
        return {'nom': 'Ambassadeur', 'points_restants': 500 - points}
    return None