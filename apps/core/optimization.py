"""
Optimisation des requêtes et des performances
"""
from functools import wraps
from django.core.cache import cache
from django.db import connection
import time
import logging

logger = logging.getLogger(__name__)


def cache_view(timeout=600):
    """
    Décorateur pour mettre en cache les vues
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Construire une clé de cache unique
            cache_key = f'view_cache_{request.path}_{request.GET.urlencode()}'
            
            if request.user.is_authenticated:
                cache_key += f'_{request.user.id}'
            
            # Vérifier si la réponse est dans le cache
            cached_response = cache.get(cache_key)
            if cached_response:
                return cached_response
            
            # Exécuter la vue
            response = view_func(request, *args, **kwargs)
            
            # Mettre en cache
            if response.status_code == 200:
                cache.set(cache_key, response, timeout)
            
            return response
        return wrapper
    return decorator


def debug_queries(func):
    """
    Décorateur pour déboguer les requêtes SQL
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Activer le débogage des requêtes
        connection.queries_log.clear()
        
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        num_queries = len(connection.queries)
        
        if num_queries > 10:
            logger.warning(
                f"Fonction {func.__name__} a exécuté {num_queries} requêtes en {execution_time:.2f}s"
            )
        
        return result
    return wrapper


class QueryOptimizer:
    """
    Optimiseur de requêtes
    """
    @staticmethod
    def optimize_projects(queryset):
        """
        Optimiser les requêtes de projets
        """
        return queryset.select_related('categorie').prefetch_related(
            'partenaires',
            'categories',
            'images'
        )
    
    @staticmethod
    def optimize_articles(queryset):
        """
        Optimiser les requêtes d'articles
        """
        return queryset.select_related('auteur').prefetch_related(
            'categories',
            'commentaires'
        )
    
    @staticmethod
    def optimize_members(queryset):
        """
        Optimiser les requêtes de membres
        """
        return queryset.select_related('fonction')
    
    @staticmethod
    def optimize_documents(queryset):
        """
        Optimiser les requêtes de documents
        """
        return queryset.select_related('categorie')