
import json

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from news_automation.models import NewsSource, NewsLead


class Command(BaseCommand):
    help = "Import exported news sources and leads safely."

    def add_arguments(self, parser):
        parser.add_argument(
            "--input",
            default="urbannews_leads_export.json",
            help="Path to the exported JSON file",
        )

    def handle(self, *args, **options):
        filename = options["input"]

        try:
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError) as exc:
            raise CommandError(
                f"Cannot read export file {filename}: {exc}"
            )

        sources = data.get("sources", [])
        leads = data.get("leads", [])

        source_map = {}
        imported = 0
        skipped = 0

        with transaction.atomic():
            for item in sources:
                source, _ = NewsSource.objects.get_or_create(
                    feed_url=item["feed_url"],
                    defaults={
                        "name": item["name"],
                        "category": item.get("category", "General"),
                        "is_active": item.get("is_active", True),
                    },
                )
                source_map[source.feed_url] = source

            for item in leads:
                feed_url = item.get("source__feed_url")
                source = source_map.get(feed_url)

                if source is None:
                    skipped += 1
                    self.stderr.write(
                        f"Skipped lead without matching source: "
                        f"{item.get('headline', 'Unknown')}"
                    )
                    continue

                source_url = item.get("source_url")

                if not source_url:
                    skipped += 1
                    continue

                _, created = NewsLead.objects.get_or_create(
                    source_url=source_url,
                    defaults={
                        "source": source,
                        "headline": item["headline"],
                        "source_published_at": item.get(
                            "source_published_at"
                        ),
                        "category": item.get(
                            "category",
                            source.category,
                        ),
                        "status": "new",
                        "original_draft": "",
                        "research_notes": "",
                        "attribution_notes": (
                            f"Imported from local news lead. "
                            f"Discovery source: {source.name}. "
                            "Research and verify before drafting."
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

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete. Imported: {imported}. "
                f"Skipped existing or unmatched leads: {skipped}."
            )
        )
