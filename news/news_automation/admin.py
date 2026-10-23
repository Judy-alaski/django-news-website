from django.contrib import admin
from .models import NewsSource, NewsLead


@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active")
    list_filter = ("is_active", "category")
    search_fields = ("name", "feed_url")


@admin.register(NewsLead)
class NewsLeadAdmin(admin.ModelAdmin):
    list_display = (
        "headline",
        "source",
        "category",
        "status",
        "facts_verified",
        "originality_checked",
        "approved_for_publication",
        "discovered_at",
    )

    list_filter = (
        "status",
        "category",
        "facts_verified",
        "originality_checked",
        "copyright_checked",
    )

    search_fields = ("headline", "original_draft")
    readonly_fields = ("discovered_at", "updated_at")

