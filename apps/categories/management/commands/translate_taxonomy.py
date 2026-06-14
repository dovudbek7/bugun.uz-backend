"""Backfill AI translations for Category and Interest titles.

These are mostly static, so this is a one-off (re-run after adding new ones).

Usage:
    python manage.py translate_taxonomy           # only missing ru/en
    python manage.py translate_taxonomy --force   # re-translate everything
"""
import time

from django.core.management.base import BaseCommand

from apps.categories.models import Category
from apps.common.ai_translate import translate_text
from apps.interests.models import Interest


class Command(BaseCommand):
    help = "Translate Category and Interest titles into ru / en via OpenAI."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Re-translate even rows that already have ru/en.")
        parser.add_argument("--sleep", type=float, default=0.5, help="Seconds to sleep between API calls.")

    def handle(self, *args, **options):
        for model, label in ((Category, "Category"), (Interest, "Interest")):
            self._translate_model(model, label, options)

    def _translate_model(self, model, label, options):
        qs = model.objects.all().order_by("id")
        done = failed = skipped = 0
        for obj in qs:
            if not options["force"] and obj.title_ru and obj.title_en:
                skipped += 1
                continue
            try:
                result = translate_text(obj.title)
            except Exception as exc:  # noqa: BLE001
                failed += 1
                self.stderr.write(f"  {label} {obj.id} FAILED: {exc}")
                continue
            if not result:
                skipped += 1
                continue
            obj.title_ru = result.get("ru", "")
            obj.title_en = result.get("en", "")
            obj.save(update_fields=["title_ru", "title_en"])
            done += 1
            self.stdout.write(f"  {label} {obj.id} ({obj.title}) -> ru/en done")
            time.sleep(options["sleep"])
        self.stdout.write(self.style.SUCCESS(f"{label}: done={done} failed={failed} skipped={skipped}"))
