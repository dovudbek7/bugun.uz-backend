# Categories, Interests, Locations

---

## Kategoriyalar

```http
GET /api/categories/
```

**Permission:** Ochiq

Pagination yo'q.

### Query Params

| Param | Misol | Izoh |
|-------|-------|------|
| `lang` | `?lang=ru` | Sarlavhani tilga moslashtiradi |

### Response `200 OK`

```json
[
  {
    "id": 1,
    "title": "Shaxmat",
    "title_ru": "Шахматы",
    "title_en": "Chess",
    "icon": "♟️",
    "color": "#1e293b"
  },
  {
    "id": 2,
    "title": "Mafiya",
    "title_ru": "Мафия",
    "title_en": "Mafia",
    "icon": "🎭",
    "color": "#7f1d1d"
  }
]
```

### Til bo'yicha `title` qiymati

`?lang=uz_cyrl` yuborilsa — `title` field kiril harfda qaytadi (lotin'dan avtomatik konvert).

```
GET /api/categories/?lang=uz_cyrl

→ title: "Шахмат" (Shaxmat'dan auto-convert)
```

---

## Kategoriyani Yaratish/Yangilash

Admin panel orqali: `/admin/categories/category/`

API orqali — faqat admin:
```http
POST /api/categories/
```

```json
{
  "title": "Shaxmat",
  "title_ru": "Шахматы",
  "title_en": "Chess",
  "icon": "♟️",
  "color": "#1e293b"
}
```

> **Qoida:** `title` fieldiga **har doim o'zbekcha** yozing (lotin). `uz_cyrl` avtomatik hisoblanadi.

---

## Qiziqishlar (Interests)

```http
GET /api/interests/
```

**Permission:** Ochiq

Pagination yo'q.

### Response `200 OK`

```json
[
  {
    "id": 1,
    "title": "Shaxmat",
    "title_ru": "Шахматы",
    "title_en": "Chess",
    "icon": "♟️"
  },
  {
    "id": 5,
    "title": "Futbol",
    "title_ru": "Футбол",
    "title_en": "Football",
    "icon": "⚽"
  }
]
```

`?lang=` parametri ishlaydi (categories'dek).

---

## Manzillar (Locations)

```http
GET /api/locations/
```

**Permission:** Ochiq

Pagination yo'q.

### Response `200 OK`

```json
[
  {
    "id": 1,
    "title": "Magic City Mall",
    "latitude": "41.299500",
    "longitude": "69.240100",
    "address": "Yunusobod, Tashkent",
    "created_at": "2026-05-15T12:00:00Z"
  }
]
```

---

## Manzil Yaratish

```http
POST /api/locations/
```

**Permission:** Faqat organizer (`is_organizer=true`)

### Request Body

```json
{
  "title": "Yangi joy",
  "latitude": 41.3100,
  "longitude": 69.2500,
  "address": "Chilonzor, Tashkent"
}
```

### Response `200 OK`

```json
{
  "message": "Location created",
  "location": {
    "id": 16,
    "title": "Yangi joy",
    "latitude": "41.310000",
    "longitude": "69.250000",
    "address": "Chilonzor, Tashkent"
  }
}
```

---

## Frontend uchun Eslatmalar

### Kategoriya bilan Event filter

```
GET /api/events/?category=1
```

### Onboarding'da interest tanlash

1. `GET /api/interests/` → ro'yxat oling
2. Foydalanuvchi tanlasin (multi-select)
3. `POST /api/auth/onboarding/` → `{ "interests": [1, 3, 5] }`

### Xarita uchun Location

Event yaratishdan oldin:
1. `GET /api/locations/` → mavjud joylar ro'yxati
2. Yo'q bo'lsa → `POST /api/locations/` → yangi yarating
3. Event yaratishda `location` ID yuboring
