"""Auto-translate event descriptions on save (admin, API, shell — all paths)."""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Event
from .tasks import translate_event

# Fields written by translate_event itself — saves limited to these must NOT
# re-trigger translation (avoids an infinite loop).
_TASK_FIELDS = {
    "description", "description_ru", "description_en",
    "translation_status", "translated_at", "updated_at",
}


@receiver(pre_save, sender=Event)
def _cache_old_description(sender, instance, **kwargs):
    if instance.pk:
        old = Event.objects.filter(pk=instance.pk).only("description").first()
        instance._old_description = old.description if old else None
    else:
        instance._old_description = None


@receiver(post_save, sender=Event)
def _translate_on_save(sender, instance, created, update_fields=None, **kwargs):
    if update_fields is not None and set(update_fields) <= _TASK_FIELDS:
        return  # task write-back or a targeted save (cancel, reminder, ...)
    old = getattr(instance, "_old_description", None)
    if not instance.description:
        return
    if created or old != instance.description:
        translate_event.delay(instance.pk)
