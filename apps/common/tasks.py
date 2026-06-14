"""Shared Celery tasks."""
from celery import shared_task
from django.apps import apps as django_apps


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def translate_taxonomy_obj(self, app_label, model_name, pk):
    """Translate a Category/Interest title into ru/en (uz_cyrl is derived)."""
    from apps.common.ai_translate import translate_text

    model = django_apps.get_model(app_label, model_name)
    obj = model.objects.filter(pk=pk).first()
    if not obj:
        return
    try:
        result = translate_text(obj.title)
    except Exception as exc:  # noqa: BLE001
        raise self.retry(exc=exc)
    if not result:
        return
    obj.title_ru = result.get("ru", "")
    obj.title_en = result.get("en", "")
    obj.save(update_fields=["title_ru", "title_en"])
