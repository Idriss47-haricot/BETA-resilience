"""
Filtres personnalisés pour les templates
"""
from django import template
from django.utils.text import Truncator
from django.utils.html import strip_tags

register = template.Library()

@register.filter
def truncate_chars(value, max_length=100):
    """
    Tronque un texte à un nombre de caractères spécifié
    """
    if not value:
        return ''
    clean_text = strip_tags(value)
    return Truncator(clean_text).chars(max_length)

@register.filter
def truncate_words(value, max_words=30):
    """
    Tronque un texte à un nombre de mots spécifié
    """
    if not value:
        return ''
    clean_text = strip_tags(value)
    return Truncator(clean_text).words(max_words)

@register.filter
def file_size(value):
    """
    Convertit une taille de fichier en format lisible
    """
    if not value:
        return '0 KB'
    size = value.size
    if size < 1024:
        return f'{size} B'
    elif size < 1024 * 1024:
        return f'{size / 1024:.1f} KB'
    elif size < 1024 * 1024 * 1024:
        return f'{size / (1024 * 1024):.1f} MB'
    else:
        return f'{size / (1024 * 1024 * 1024):.1f} GB'