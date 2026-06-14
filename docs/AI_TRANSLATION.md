# AI Translation

Event tavsiflari va kategoriya/qiziqish nomlari OpenAI (`gpt-4o-mini`) orqali
avtomatik tarjima qilinadi. Frontend `Accept-Language` header yuboradi, backend
o'sha tilga mos bitta qiymat qaytaradi.

## Languages

| Kod        | Manba                                   |
|------------|-----------------------------------------|
| `uz_latn`  | Kanonik. AI normalize qiladi.           |
| `ru`       | AI                                      |
| `en`       | AI                                      |
| `uz_cyrl`  | **Avtomatik** — `latin_to_cyrillic(uz_latn)`, saqlanmaydi |

AI har doim faqat **3 til** chiqaradi (`uz_latn`, `ru`, `en`). Kiril alifbosi
koddan generatsiya bo'ladi (`apps/telegram_bot/translations.py`).

## Setup

`.env`:
```
CHATGPT_API_KEY=sk-...           # OpenAI kalit (majburiy)
OPENAI_TRANSLATE_MODEL=gpt-4o-mini   # ixtiyoriy, default shu
```
```
pip install -r requirements.txt   # openai qo'shilgan
```

Settings: `config/settings.py` → `OPENAI_API_KEY`, `OPENAI_TRANSLATE_MODEL`.

## Frontend kontrakt

Har bir so'rovda til header'da yuboriladi:
```
Accept-Language: ru
```
Qo'llab-quvvatlanadigan qiymatlar: `uz_latn`, `uz_cyrl`, `ru`, `en`
(`uz`, `uz-Cyrl`, `en-US` kabilar ham normalize qilinadi).

Javobda field nomi **o'zgarmaydi** — `description` (yo `name`/`title`) bitta
mos tilli qiymat sifatida keladi. `description_ru`/`description_en` frontendga
ko'rinmaydi.

Tarjima yo'q/tugamagan bo'lsa → kanonik `uz_latn` ga fallback (bo'sh emas).

Til aniqlash prioriteti (`apps/common/lang.py`):
`Accept-Language` header → `?lang=` query → `user.language` → `uz_latn`.

## Oqim (yangi event)

```
POST /api/events/  (user description, istalgan til)
        │
        ▼
EventViewSet.create  →  translate_event.delay(event_id)   (Celery)
        │
        ▼
translate_text()  →  OpenAI  →  {uz_latn, ru, en}
        │
        ▼
description (uz_latn) + description_ru + description_en saqlanadi
translation_status: pending → done
        │
        ▼
GET /api/events/<id>/  +  Accept-Language: ru  →  { "description": "<ru>" }
```

`update`da `description` o'zgarsa → qayta tarjima triggeri.

## Management komandalar

Eski eventlarni to'ldirish:
```
python manage.py translate_events            # pending/failed lar
python manage.py translate_events --all      # hammasi qayta
python manage.py translate_events --limit 5  # test uchun
```

Kategoriya + qiziqishlar:
```
python manage.py translate_taxonomy          # bo'sh ru/en lar
python manage.py translate_taxonomy --force  # hammasi qayta
```

Ikkalasida ham `--sleep` (default 0.5s) rate-limit uchun.

## Admin

- **Event**: `translation_status` ustun + filtr; `description_uz_cyrl`
  (computed, readonly) ko'rinadi; `ru`/`en` tahrirlanadi; action
  "Re-translate selected events (AI)".
- **Category / Interest**: `title_ru`/`title_en` ustun + tahrir,
  `title_uz_cyrl` readonly, action "Re-translate selected (AI, ru/en)".

## Narx

`gpt-4o-mini`, 4-5 qator matn, 3 til ≈ **$0.00025 / event**.
$3 ≈ ~12,000 event.
