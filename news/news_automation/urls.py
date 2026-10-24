
from django.urls import path
from . import views

urlpatterns = [
    path(
        "import-leads/",
        views.import_news_leads,
        name="import_news_leads",
    ),
]
