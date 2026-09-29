"""
Middleware personnalisé pour la sécurité
"""
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.conf import settings
import re
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Ajouter des headers de sécurité supplémentaires
    """
    def process_response(self, request, response):
        # Content Security Policy
        # À ajuster selon les besoins
        csp = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com",
            "font-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com",
            "img-src 'self' data: https://*",
            "frame-src 'self' https://www.google.com https://www.youtube.com",
            "connect-src 'self'",
        ]
        response['Content-Security-Policy'] = '; '.join(csp)
        
        # Autres headers de sécurité
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        response['Cross-Origin-Opener-Policy'] = 'same-origin'
        response['Cross-Origin-Embedder-Policy'] = 'require-corp'
        
        return response


class UserAgentBlockMiddleware(MiddlewareMixin):
    """
    Bloquer les User Agents malveillants
    """
    BLOCKED_USER_AGENTS = [
        r'(?i)sqlmap',
        r'(?i)nikto',
        r'(?i)wpscan',
        r'(?i)python-requests',
        r'(?i)curl',
        r'(?i)wget',
        r'(?i)scrapy',
        r'(?i)burp',
        r'(?i)zap',
        r'(?i)acunetix',
    ]
    
    def process_request(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        for pattern in self.BLOCKED_USER_AGENTS:
            if re.search(pattern, user_agent):
                logger.warning(f"User Agent bloqué: {user_agent} - IP: {request.META.get('REMOTE_ADDR')}")
                return HttpResponseForbidden('Accès refusé.')
        
        return None


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware de rate limiting simple
    """
    def process_request(self, request):
        # Implémentation avec django-ratelimit ou personnalisée
        pass