from django.contrib import admin
from .models import Comment
from .models import Category, Author, Article

admin.site.register(Category)
admin.site.register(Author)
admin.site.register(Article)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'article',
        'approved',
        'created_at',
    )

    list_filter = (
        'approved',
        'created_at',
    )

    fields = (
        'article',
        'parent',
        'name',
        'email',
        'content',
        'approved',
    )

    search_fields = (
        'name',
        'email',
        'content',
        'article__title',
    )

    list_editable = (
        'approved',
    )

    ordering = (
        '-created_at',
    )
