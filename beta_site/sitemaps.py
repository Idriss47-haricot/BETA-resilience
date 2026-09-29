from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        # Remplacez 'forums:index' par le nom de votre vue principale
        return ['forums:index']

    def location(self, item):
        return reverse(item)
