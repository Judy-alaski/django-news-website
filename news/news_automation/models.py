from django.db import models
from django.utils import timezone


class NewsSource(models.Model):
    name = models.CharField(max_length=200)
    feed_url = models.URLField(unique=True)
    category = models.CharField(max_length=100, default="General")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class NewsLead(models.Model):

    STATUS_CHOICES = [
        ("new", "New"),
        ("review", "Needs Research"),
        ("draft", "Draft Prepared"),
        ("rejected", "Rejected"),
        ("used", "Article Published"),
    ]

    source = models.ForeignKey(
        NewsSource,
        on_delete=models.PROTECT,
        related_name="leads",
    )

    headline = models.CharField(max_length=500)
    source_url = models.URLField(max_length=1000, unique=True)
    source_published_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    category = models.CharField(
        max_length=100,
        default="General",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
    )

    # Our independently written draft, not copied source text.
    original_draft = models.TextField(blank=True)

    # Research links and factual verification notes.
    research_notes = models.TextField(blank=True)

    # Record the sources used to verify the story.
    attribution_notes = models.TextField(blank=True)

    # Drafts cannot be published until reviewed.
    originality_checked = models.BooleanField(default=False)
    facts_verified = models.BooleanField(default=False)
    copyright_checked = models.BooleanField(default=False)
    approved_for_publication = models.BooleanField(default=False)

    discovered_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-discovered_at"]

    def __str__(self):
        return self.headline

