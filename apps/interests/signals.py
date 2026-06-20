"""Auto-translate interest titles on save (admin, API, shell — all paths)."""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.common.tasks import translate_taxonomy_obj

from .models import Interest

_TASK_FIELDS = {"title_ru", "title_en"}


@receiver(pre_save, sender=Interest)
def _cache_old_title(sender, instance, **kwargs):
    if instance.pk:
        old = Interest.objects.filter(pk=instance.pk).only("title").first()
        instance._old_title = old.title if old else None
    else:
        instance._old_title = None


@receiver(post_save, sender=Interest)
def _translate_on_save(sender, instance, created, update_fields=None, **kwargs):
    if update_fields is not None and set(update_fields) <= _TASK_FIELDS:
        return  # task write-back
    old = getattr(instance, "_old_title", None)
    if not instance.title:
        return
    if created or old != instance.title:
        translate_taxonomy_obj.delay("interests", "Interest", instance.pk)
