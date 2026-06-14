"""Backfill AI translations for existing events.

Usage:
    python manage.py translate_events            # only pending/failed events
    python manage.py translate_events --all      # re-translate everything
    python manage.py translate_events --limit 5  # cap for testing
"""
import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.common.ai_translate import translate_text
from apps.events.models import Event


class Command(BaseCommand):
    help = "Translate existing event descriptions into uz_latn / ru / en via OpenAI."

    def add_arguments(self, parser):
        parser.add_argument("--all", action="store_true", help="Re-translate all events, not just pending/failed.")
        parser.add_argument("--limit", type=int, default=0, help="Maximum number of events to process (0 = no limit).")
        parser.add_argument("--sleep", type=float, default=0.5, help="Seconds to sleep between API calls.")

    def handle(self, *args, **options):
        qs = Event.objects.all().order_by("id")
        if not options["all"]:
            qs = qs.exclude(translation_status=Event.TRANSLATION_DONE)
        if options["limit"]:
            qs = qs[: options["limit"]]

        total = qs.count()
        self.stdout.write(f"Translating {total} event(s)...")
        done = failed = skipped = 0

        for index, event in enumerate(qs, start=1):
            try:
                result = translate_text(event.description)
            except Exception as exc:  # noqa: BLE001
                event.translation_status = Event.TRANSLATION_FAILED
                event.save(update_fields=["translation_status", "updated_at"])
                failed += 1
                self.stderr.write(f"  [{index}/{total}] event {event.id} FAILED: {exc}")
                continue

            if not result:
                skipped += 1
                self.stdout.write(f"  [{index}/{total}] event {event.id} skipped (empty)")
                continue

            event.description = result.get("uz_latn") or event.description
            event.description_ru = result.get("ru", "")
            event.description_en = result.get("en", "")
            event.translation_status = Event.TRANSLATION_DONE
            event.translated_at = timezone.now()
            event.save(update_fields=[
                "description", "description_ru", "description_en",
                "translation_status", "translated_at", "updated_at",
            ])
            done += 1
            self.stdout.write(f"  [{index}/{total}] event {event.id} done")
            time.sleep(options["sleep"])

        self.stdout.write(self.style.SUCCESS(f"Finished. done={done} failed={failed} skipped={skipped}"))
