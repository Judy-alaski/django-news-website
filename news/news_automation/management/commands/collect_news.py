import calendar
import logging
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit

import feedparser

from django.core.management.base import BaseCommand
from django.utils import timezone as django_timezone

from news_automation.models import NewsSource, NewsLead


logger = logging.getLogger(__name__)


def clean_article_url(url):
    """
    Normalize basic URL components for duplicate detection.
    Do not remove query parameters because some URLs need them.
    """
    if not url:
        return ""

    parts = urlsplit(url.strip())

    if parts.scheme.lower() not in ("http", "https"):
        return ""

    if not parts.netloc:
        return ""

    return urlunsplit((
        parts.scheme.lower(),
        parts.netloc.lower(),
        parts.path or "/",
        parts.query,
        "",  # Remove fragment only.
    ))


def get_published_date(entry):
    """
    Read the RSS publication date if available.
    Otherwise return None.
    """
    parsed = (
        entry.get("published_parsed")
        or entry.get("updated_parsed")
    )

    if not parsed:
        return None

    try:
        timestamp = calendar.timegm(parsed)

        return datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc,
        )
    except (ValueError, OverflowError, OSError):
        return None


class Command(BaseCommand):
    help = "Collect news headlines and links from approved RSS feeds."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            type=int,
            help="Collect from one NewsSource ID only.",
        )

        parser.add_argument(
            "--limit",
            type=int,
            default=30,
            help="Maximum entries examined per feed (default: 30).",
        )

    def handle(self, *args, **options):
        source_id = options.get("source")
        limit = options["limit"]

        if limit < 1:
            self.stderr.write(
                self.style.ERROR("--limit must be at least 1.")
            )
            return

        sources = NewsSource.objects.filter(is_active=True)

        if source_id:
            sources = sources.filter(pk=source_id)

        if not sources.exists():
            self.stdout.write(
                self.style.WARNING(
                    "No active news sources found."
                )
            )
            return

        total_created = 0
        total_skipped = 0

        for source in sources:
            self.stdout.write(
                f"Checking feed: {source.name}"
            )

            try:
                feed = feedparser.parse(
                    source.feed_url,
                    request_headers={
                        "User-Agent": "UrbanNewsRSSCollector/1.0"
                    },
                )
            except Exception as exc:
                logger.exception(
                    "Could not read feed %s",
                    source.name,
                )
                self.stderr.write(
                    f"Feed error for {source.name}: {exc}"
                )
                continue

            if getattr(feed, "bozo", False):
                self.stderr.write(
                    self.style.WARNING(
                        f"Feed may be malformed: {source.name}"
                    )
                )

            entries = feed.entries[:limit]
            created_for_source = 0

            for entry in entries:
                headline = (entry.get("title") or "").strip()
                article_url = clean_article_url(
                    entry.get("link", "")
                )

                # Collect only headline and link.
                # Do not ingest article body or full descriptions.
                if not headline or not article_url:
                    total_skipped += 1
                    continue

                if NewsLead.objects.filter(
                    source_url=article_url
                ).exists():
                    total_skipped += 1
                    continue

                published_at = get_published_date(entry)

                try:
                    _, created = NewsLead.objects.get_or_create(
                        source_url=article_url,
                        defaults={
                            "source": source,
                            "headline": headline[:500],
                            "source_published_at": published_at,
                            "category": source.category,
                            "status": "new",
                            "original_draft": "",
                            "research_notes": "",
                            "attribution_notes": (
                                f"Discovery source: {source.name}. "
                                "Verify the original reporting and "
                                "other reliable sources before drafting."
                            ),
                            "originality_checked": False,
                            "facts_verified": False,
                            "copyright_checked": False,
                            "approved_for_publication": False,
                        },
                    )
                except Exception:
                    logger.exception(
                        "Could not save feed entry: %s",
                        article_url,
                    )
                    total_skipped += 1
                    continue

                if created:
                    created_for_source += 1
                    total_created += 1
                else:
                    total_skipped += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"{source.name}: "
                    f"{created_for_source} new leads saved."
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished. New leads: {total_created}. "
                f"Skipped entries: {total_skipped}."
            )
        )
