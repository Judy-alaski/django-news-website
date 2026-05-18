from django.db import models
from django.contrib.auth.models import User
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
    content = RichTextUploadingField()
    
    image = models.ImageField(
    storage=MediaCloudinaryStorage(),
    upload_to='articles/',
    blank=True,
    null=True
    )
    #image = models.ImageField(upload_to='articles/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles')
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    published_date = models.DateTimeField(auto_now_add=True)
    is_breaking = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email    

