"""
Gestion des méta-données pour le SEO
"""
from django.views.generic import View
from django.template.loader import render_to_string
from django.core.exceptions import ImproperlyConfigured


class MetaMixin(View):
    """
    Mixin pour ajouter des méta-données à toutes les vues
    """
    meta_title = None
    meta_description = None
    meta_keywords = None
    meta_robots = 'index, follow'
    og_title = None
    og_description = None
    og_image = None
    
    def get_meta_title(self, context=None):
        if self.meta_title:
            return self.meta_title
        if context and 'object' in context:
            obj = context['object']
            if hasattr(obj, 'meta_titre') and obj.meta_titre:
                return obj.meta_titre
            if hasattr(obj, 'titre'):
                return obj.titre
        return None
    
    def get_meta_description(self, context=None):
        if self.meta_description:
            return self.meta_description
        if context and 'object' in context:
            obj = context['object']
            if hasattr(obj, 'meta_description') and obj.meta_description:
                return obj.meta_description
            if hasattr(obj, 'description_courte'):
                return obj.description_courte
            if hasattr(obj, 'extrait'):
                return obj.extrait
        return None
    
    def get_meta_keywords(self, context=None):
        if self.meta_keywords:
            return self.meta_keywords
        if context and 'object' in context:
            obj = context['object']
            if hasattr(obj, 'meta_keywords') and obj.meta_keywords:
                return obj.meta_keywords
            if hasattr(obj, 'tags'):
                return obj.tags
        return None
    
    def get_og_image(self, context=None):
        if self.og_image:
            return self.og_image
        if context and 'object' in context:
            obj = context['object']
            if hasattr(obj, 'image_couverture') and obj.image_couverture:
                return obj.image_couverture.url
            if hasattr(obj, 'image_principale') and obj.image_principale:
                return obj.image_principale.url
            if hasattr(obj, 'logo') and obj.logo:
                return obj.logo.url
        return None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Ajouter les méta-données au contexte
        context['meta_title'] = self.get_meta_title(context)
        context['meta_description'] = self.get_meta_description(context)
        context['meta_keywords'] = self.get_meta_keywords(context)
        context['meta_robots'] = self.meta_robots
        context['og_title'] = self.get_meta_title(context)
        context['og_description'] = self.get_meta_description(context)
        context['og_image'] = self.get_og_image(context)
        
        return context


class RobotsTxtView(View):
    """
    Vue pour générer le fichier robots.txt
    """
    def get(self, request):
        content = """
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /login/
Disallow: /logout/
Disallow: /password-reset/
Sitemap: https://beta-resilience.org/sitemap.xml

# Bloquer les bots malveillants
User-agent: SemrushBot
Disallow: /

User-agent: AhrefsBot
Disallow: /

User-agent: MJ12bot
Disallow: /

User-agent: DotBot
Disallow: /
"""
        return HttpResponse(content, content_type='text/plain')