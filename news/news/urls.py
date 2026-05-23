"""
URL configuration for news project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from newsApp.sitemaps import ArticleSitemap
from newsApp.models import Article

info_dict = {
    'queryset': Article.objects.all(),
    'date_field': 'published_date',  # make sure this field exists
}

sitemaps = {
    'articles': ArticleSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('newsApp.urls')),

    path('ckeditor/', include('ckeditor_uploader.urls')),

    path(
        'robots.txt',
        TemplateView.as_view(
            template_name='robots.txt',
            content_type='text/plain'
        ),
    ),

    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'
    ),
]



#urlpatterns = [
    #path('admin/', admin.site.urls),
    #path('', include('newsApp.urls')),
    #path('ckeditor/', include('ckeditor_uploader.urls')),
    #path('sitemap.xml',sitemap,{'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    #path("robots.txt"#,TemplateView.as_view(template_name="robots.txt",content_type="text/plain")),
#]

