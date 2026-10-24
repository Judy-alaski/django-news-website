
import json

from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder

from news_automation.models import NewsSource, NewsLead


class Command(BaseCommand):
    help = "Export news sources and leads to a JSON file."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default="urbannews_leads_export.json",
            help="Output JSON filename",
        )

    def handle(self, *args, **options):
        data = {
            "sources": list(
                NewsSource.objects.values(
                    "name",
                    "feed_url",
                    "category",
                    "is_active",
                )
            ),
            "leads": list(
                NewsLead.objects.values(
                    "source__feed_url",
                    "headline",
                    "source_url",
                    "source_published_at",
                    "category",
                    "status",
                    "original_draft",
                    "research_notes",
                    "attribution_notes",
                    "originality_checked",
                    "facts_verified",
                    "copyright_checked",
                    "approved_for_publication",
                    "discovered_at",
                )
            ),
        }

        with open(options["output"], "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
                cls=DjangoJSONEncoder,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Exported {len(data['sources'])} sources and "
                f"{len(data['leads'])} leads to "
                f"{options['output']}"
            )
        )
