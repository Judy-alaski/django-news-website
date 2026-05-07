from .models import Article

def breaking_news_processor(request):
    breaking_news = Article.objects.filter(is_breaking=True).order_by('-published_date')[:5]
    return {'breaking_news': breaking_news}