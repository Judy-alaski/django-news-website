from django.contrib.sitemaps import Sitemap
from .models import Article

class ArticleSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Article.objects.all().order_by('-published_date')

    def lastmod(self, obj):
        return obj.published_date