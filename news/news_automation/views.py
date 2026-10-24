from django.shortcuts import render

import json

from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .models import NewsSource, NewsLead


@staff_member_required
@require_http_methods(["GET", "POST"])
def import_news_leads(request):
    if request.method == "GET":
        return render(
            request,
            "news_automation/import_news_leads.html",
        )

    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        return JsonResponse(
            {"error": "Please select a JSON file."},
            status=400,
        )

    if uploaded_file.size > 2 * 1024 * 1024:
        return JsonResponse(
            {"error": "File exceeds the 2 MB limit."},
            status=400,
        )

    try:
        data = json.load(uploaded_file)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "The uploaded file is not valid JSON."},
            status=400,
        )

    if not isinstance(data, dict):
        return JsonResponse(
            {"error": "Unexpected export format."},
            status=400,
        )

    sources = data.get("sources", [])
    leads = data.get("leads", [])

    if not isinstance(sources, list) or not isinstance(leads, list):
        return JsonResponse(
            {"error": "Invalid sources or leads data."},
            status=400,
        )

    if len(sources) > 100 or len(leads) > 1000:
        return JsonResponse(
            {"error": "The export contains too many records."},
            status=400,
        )

    imported = 0
    skipped = 0

    try:
        with transaction.atomic():
            source_map = {}

            for item in sources:
                if not isinstance(item, dict):
                    raise ValueError("Invalid source record.")

                feed_url = item.get("feed_url")
                name = item.get("name")

                if not feed_url or not name:
                    raise ValueError("Source name or feed URL is missing.")

                source, _ = NewsSource.objects.get_or_create(
                    feed_url=feed_url,
                    defaults={
                        "name": name,
                        "category": item.get("category", "General"),
                        "is_active": bool(item.get("is_active", True)),
                    },
                )

                source_map[source.feed_url] = source

            for item in leads:
                if not isinstance(item, dict):
                    raise ValueError("Invalid news lead record.")

                feed_url = item.get("source__feed_url")
                source_url = item.get("source_url")
                headline = item.get("headline")

                source = source_map.get(feed_url)

                if not source or not source_url or not headline:
                    skipped += 1
                    continue

                _, created = NewsLead.objects.get_or_create(
                    source_url=source_url,
                    defaults={
                        "source": source,
                        "headline": headline[:500],
                        "source_published_at": item.get(
                            "source_published_at"
                        ),
                        "category": item.get(
                            "category", source.category
                        ),
                        "status": "new",
                        "original_draft": "",
                        "research_notes": "",
                        "attribution_notes": (
                            f"Imported from local export. "
                            f"Discovery source: {source.name}. "
                            "Verify facts and copyright before drafting."
                        ),
                        "originality_checked": False,
                        "facts_verified": False,
                        "copyright_checked": False,
                        "approved_for_publication": False,
                    },
                )

                if created:
                    imported += 1
                else:
                    skipped += 1

    except (ValueError, TypeError) as exc:
        return JsonResponse(
            {"error": str(exc)},
            status=400,
        )

    return JsonResponse({
        "success": True,
        "imported": imported,
        "skipped": skipped,
        "message": "Import completed. All imported leads remain unapproved.",
    })

