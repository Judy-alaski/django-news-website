from django.db import migrations
from django.utils.text import slugify


def generate_slugs(apps, schema_editor):
    Article = apps.get_model('newsApp', 'Article')

    for article in Article.objects.all():
        if not article.slug:
            article.slug = slugify(article.title)[:255]
            article.save()


class Migration(migrations.Migration):

    dependencies = [
        ('newsApp', '0011_alter_article_slug'),
    ]

    operations = [
        migrations.RunPython(generate_slugs),
    ]
