# Backend Overview

## Base URL

```
http://localhost:8000
```

Production'da domain bilan almashtiriladi.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API | Django REST Framework |
| Auth | JWT (SimpleJWT) |
| Database | PostgreSQL (SQLite dev uchun) |
| Cache/Queue | Redis |
| Background tasks | Celery |
| Telegram Bot | aiogram 3.x |
| Docs | Swagger — `/api/docs/` |

---

## API Prefix

Barcha REST endpointlar `/api/` bilan boshlanadi.

```
/api/auth/telegram/
/api/events/
/api/profile/me/
...
```

---

## Authentication

JWT Bearer token ishlatiladi.

```http
Authorization: Bearer <access_token>
```

Token `POST /api/auth/telegram/` orqali olinadi.

Token muddati:
- `access` — 60 daqiqa
- `refresh` — 14 kun

---

## Response Format

### Success
```json
{ "key": "value" }
```

### List (paginated)
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/events/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

### Error
```json
{ "detail": "Error message here." }
```
yoki field-level:
```json
{ "field_name": ["Error text."] }
```

---

## HTTP Status Codes

| Code | Ma'nosi |
|------|---------|
| 200 | OK |
| 201 | Created |
| 400 | Validation error |
| 401 | Token yo'q yoki noto'g'ri |
| 403 | Ruxsat yo'q |
| 404 | Topilmadi |

---

## Pagination

Default: 20 ta per page.

```
GET /api/events/?page=2&page_size=10
```

---

## Language Support

### API orqali
Query param yuboring:
```
GET /api/categories/?lang=uz_latn
GET /api/categories/?lang=uz_cyrl
GET /api/categories/?lang=ru
GET /api/categories/?lang=en
```

Agar `lang` yuborilmasa — logged-in user'ning saqlangan tili ishlatiladi.

### Mavjud tillar
| Kod | Til |
|-----|-----|
| `uz_latn` | O'zbek (lotin) — **default** |
| `uz_cyrl` | O'zbek (kiril) — lotin'dan auto-konvert |
| `ru` | Ruscha |
| `en` | Inglizcha |

---

## Swagger Docs

```
GET /api/docs/
```

Barcha endpointlarni interaktiv test qilish mumkin.

---

## Admin Dashboard

```
/admin/              → Django admin panel
/dashboard/statistics/ → Custom statistika sahifasi
/dashboard/reports/    → Reportlar sahifasi
```

Faqat `is_staff=True` adminlar kira oladi.
