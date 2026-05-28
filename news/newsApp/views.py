from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.urls import reverse
from django.http import HttpResponseRedirect
from .forms import CategoryForm, ArticleForm
from .models import Category, Article
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .forms import SignupForm
from .models import Author
from django.http import HttpResponse
from .models import NewsletterSubscriber
from .forms import LoginForm
from django.contrib.auth import logout
from django.contrib.admin.views.decorators import staff_member_required

from django.shortcuts import render
from .models import Article, Category

def home(request):
    all_articles = Article.objects.all().order_by('-published_date')

    breaking_news = all_articles.filter(is_breaking=True)[:10]
    top_stories = all_articles[:8]
    lead_articles = Article.objects.filter(published_date__lte=now()).exclude(image='').order_by('-published_date')[:1]

    # Paginate only top stories
    paginator = Paginator(all_articles, 6)  # Show 6 per page
    page_number = request.GET.get('page')
    top_stories = paginator.get_page(page_number)

    recent_articles = all_articles[:10]
    trending_articles = all_articles[:6]

    # MOST VIEWED ARTICLES
    most_viewed = Article.objects.order_by(
        '-views'
    )[:5]

    # Filter articles by category
    politics_articles = all_articles.filter(category__name="Politics")[:5]
    sports_articles = all_articles.filter(category__name="Sports")[:5]
    entertainment_articles = all_articles.filter(category__name="Entertainment")[:5]

    categories = Category.objects.all()

    return render(request, 'newsApp/home.html', {
        'breaking_news': breaking_news,
        'top_stories': top_stories,
        'lead_articles': lead_articles,
        'recent_articles': recent_articles,
         'most_viewed': most_viewed,
        'trending_articles': trending_articles,
        'categories_articles': {
            "Politics": politics_articles,
            "Sports": sports_articles,
            "Entertainment": entertainment_articles,
        },
        'categories': categories,
    })

def category_articles(request, category_name):
    category = get_object_or_404(Category, name=category_name)
    articles = Article.objects.filter(category=category).order_by('-published_date')
    return render(request, 'newsApp/category_articles.html', {
        'category': category,
        'articles': articles,
    })


def article_detail(request, slug):
    # Fetch article using slug
    article = get_object_or_404(Article, slug=slug)

     # increase views
    article.views += 1
    article.save()

    related_articles = Article.objects.filter(
        category=article.category
    ).exclude(id=article.id).order_by('-published_date')[:4]

    # tag recommendation system
    tags = article.tags.split(',')

    recommended_articles = Article.objects.filter(
        Q(tags__icontains=tags[0].strip())
    ).exclude(id=article.id).distinct()[:4]

    return render(request, 'newsApp/article_detail.html', {
        'article': article,
        'related_articles': related_articles,
        'recommended_articles': recommended_articles,
    })

def redirect_old_article(request, id):
    article = get_object_or_404(Article, id=id)

    return redirect('article_detail', slug=article.slug)    

def article_upload(request):
    if request.method == 'POST' and request.FILES:
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    else:
        form = ArticleForm()
    return render(request, 'article_upload.html', {'form': form})

def load_more_articles(request):
    page = request.GET.get('page')
    articles = Article.objects.all().order_by('-published_date')
    paginator = Paginator(articles, 8)  # 4 per row × 2 rows
    try:
        next_page_articles = paginator.page(page)
    except:
        return JsonResponse({'html': ''})

    html = render_to_string('newsApp/includes/top_stories_grid.html', {'top_stories': next_page_articles})
    return JsonResponse({'html': html})  

def trending_articles_view(request):
    categories = Category.objects.all()
    trending_by_category = {}

    for category in categories:
        articles = Article.objects.filter(
            category=category
        ).order_by('-published_date')[:12] 
        if articles.exists():
            trending_by_category[category.name] = articles

    return render(request, 'newsApp/trending_articles.html', {
        'trending_by_category': trending_by_category,
    }) 

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            form.add_error(None, 'Invalid credentials')
    else:
        form = LoginForm()        
    return render(request, 'newsApp/login.html') 

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'newsApp/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def search_articles(request):
    query = request.GET.get('q')

    results = Article.objects.filter(
        Q(title__icontains=query) |
        Q(content__icontains=query) |
        Q(tags__icontains=query)
    ).distinct()

    return render(request, 'newsApp/search_results.html', {
        'query': query,
        'results': results
    })

#def search_view(request):
    #query = request.GET.get('q', '') 
    #results = []

    #if query:
        #results = Article.objects.filter(
            #Q(title__icontains=query) | Q(content__icontains=query)
        #).order_by('-published_date')  

    #context = {
        #'query': query,
        #'results': results,
    #}
    #return render(request, 'newsApp/search_results.html', context)

def newsletter_signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if not NewsletterSubscriber.objects.filter(email=email).exists():
            NewsletterSubscriber.objects.create(email=email)
            messages.success(request, "Subscription successful!")

    #return redirect('/')


@login_required
#@staff_member_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully.")
            return redirect('home')
    else:
        form = CategoryForm()
    return render(request, 'newsApp/add_category.html', {'form': form})

@login_required(login_url='login')
#@staff_member_required
def add_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            author, created = Author.objects.get_or_create(user=request.user)
            article = form.save(commit=False)
            article.author = author
            article.save()
            messages.success(request, "Article added successfully.")
            return redirect('home')
        
    else:
        form = ArticleForm()
    return render(request, 'newsApp/add_article.html', {'form': form})

@login_required
#@staff_member_required
def update_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'newsApp/update_category.html', {'form': form})

@login_required
#@staff_member_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted successfully.")
        return redirect('category_list')
    return render(request, 'newsApp/delete_category.html', {'category': category})

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'newsApp/category_list.html', {'categories': categories})

# Custom admin-required decorator
def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, "You do not have permission to access this page.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def about(request):
    return render(request, 'newsApp/about.html')

def contact(request):
    return render(request, 'newsApp/contact.html')

def privacy(request):
    return render(request, 'newsApp/privacy.html')

def terms(request):
    return render(request, 'newsApp/terms.html')    

def robots_txt(request):
    data = """
    User-agent: *
    Allow: /
    Sitemap: https://urbannews-xz7c.onrender.com/sitemap.xml
    """
    return HttpResponse(data, content_type="text/plain")
