from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from cloudinary_storage.storage import MediaCloudinaryStorage
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)    

    def __str__(self):
        return self.user.username

class Article(models.Model):
    title = models.CharField(max_length=200)

    slug = models.SlugField(blank=True, null=True, max_length=255)

    content = RichTextUploadingField()

    image = models.ImageField(
        storage=MediaCloudinaryStorage(),
        upload_to='articles/',
        blank=True,
        null=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='articles'
    )

    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    summary = models.TextField(max_length=300, blank=True)

    views = models.PositiveIntegerField(default=0)

    tags = models.CharField(max_length=300, blank=True)

    published_date = models.DateTimeField(auto_now_add=True)

    is_breaking = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})
    
class Comment(models.Model):

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    name = models.CharField(max_length=100)

    email = models.EmailField(blank=True)

    content = models.TextField()

    approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.name} - {self.article.title}' 
    
class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email    

