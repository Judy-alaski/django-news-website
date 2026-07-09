from django.urls import path
from . import views

urlpatterns = [
    # Home and General Views
    path('', views.home, name='home'),
    path('search_view/', views.search_view, name='search_view'),
    path('trending/', views.trending_articles_view, name='trending_articles'),
    #path('newsletter-signup/', views.newsletter_signup, name='newsletter_signup'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy-policy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),


    # Article Views
    #path('article/<int:id>/', views.article_detail, name='article_detail'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('article/<slug:slug>/', views.redirect_old_article),
    path('upload/', views.article_upload, name='article_upload'),
    path('add_article/', views.add_article, name='add_article'),

    # Category Views
    path('category/<str:category_name>/', views.category_articles, name='category_articles'),
    path('add_category/', views.add_category, name='add_category'),
    path('update_category/<int:pk>/', views.update_category, name='update_category'),
    path('delete_category/<int:pk>/', views.delete_category, name='delete_category'),
    path('category_list/', views.category_list, name='category_list'),

    # User Authentication
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    path(
        'mobile-add-article/',
        views.mobile_article_upload,
        name='mobile_add_article'
    ),

    path(
        'article/<slug:slug>/comment/',
        views.post_comment,
        name='post_comment'
    ),
]
