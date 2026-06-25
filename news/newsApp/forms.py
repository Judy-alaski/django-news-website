from django import forms
from .models import Category, Article
from .models import Comment
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'category', 'image', 'author']
        widgets = {
            'content': CKEditorUploadingWidget(),
        }

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment

        fields = [
            'name',
            'email',
            'content'
        ]

        widgets = {

            'name': forms.TextInput(
                attrs={
                    'class':'form-control',
                    'placeholder':'Your Name'
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'class':'form-control',
                    'placeholder':'Email (Optional)'
                }
            ),

            'content': forms.Textarea(
                attrs={
                    'class':'form-control',
                    'rows':5,
                    'placeholder':'Join the discussion...'
                }
            ),

        }

class MobileArticleForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control mobile-editor',
                'rows': 30,
                'placeholder': 'Write or paste your article here...',
                'spellcheck': 'true',
                'autocomplete': 'off',
            }
        )
    )

    class Meta:
        model = Article
        fields = ['title', 'content', 'category', 'image', 'author']
