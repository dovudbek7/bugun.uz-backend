# Events API

---

## Event Object

```json
{
  "id": 1,
  "title": "Chess Championship #1",
  "description": "Join us for exciting chess!",
  "image": "http://localhost:8000/media/events/img.jpg",
  "category": {
    "id": 1,
    "title": "Shaxmat",
    "title_ru": "Шахматы",
    "title_en": "Chess",
    "icon": "♟️",
    "color": "#1e293b"
  },
  "location": {
    "id": 1,
    "title": "Magic City Mall",
    "latitude": "41.299500",
    "longitude": "69.240100",
    "address": "Yunusobod, Tashkent"
  },
  "event_date": "2026-05-20",
  "event_time": "18:00:00",
  "total_seats": 12,
  "seats_left": 7,
  "status": "upcoming",
  "participants": [
    { "id": 3, "avatar": "https://..." },
    { "id": 5, "avatar": "" }
  ],
  "organizer": {
    "id": 2,
    "full_name": "Jasur Toshmatov"
  }
}
```

> `seats_left` — dinamik hisoblanadi: `total_seats - joined_count`. DB'da saqlanmaydi.

---

## Event Status

| Qiymat | Ma'no |
|--------|-------|
| `upcoming` | Kelayotgan |
| `completed` | Tugagan |
| `cancelled` | Bekor qilingan |

---

## Eventlar Ro'yxati

```http
GET /api/events/
```

**Permission:** Ochiq

### Query Params

| Param | Misol | Izoh |
|-------|-------|------|
| `page` | `?page=2` | Sahifa raqami |
| `page_size` | `?page_size=10` | Har sahifada nechta |
| `category` | `?category=1` | Category ID bo'yicha filter |
| `status` | `?status=upcoming` | Status bo'yicha filter |
| `today` | `?today=true` | Faqat bugungi eventlar |
| `lang` | `?lang=ru` | Til (category nomi uchun) |

### Response `200 OK`

```json
{
  "count": 30,
  "next": "http://localhost:8000/api/events/?page=2",
  "previous": null,
  "results": [ ...event objects... ]
}
```

---

## Bugungi Eventlar

```http
GET /api/events/today/
```

**Permission:** Ochiq

Faqat bugungi `upcoming` statusli eventlar. Pagination yo'q.

---

## Xaritadagi Eventlar

```http
GET /api/maps/
```

**Permission:** Ochiq

`upcoming` statusli barcha eventlar koordinatlari bilan. Map sahifasi uchun.

### Response

```json
[
  {
    "id": 1,
    "name": "Chess Championship",
    "icon": "♟️",
    "time": "18:00:00",
    "seats_left": 5,
    "location": {
      "title": "Magic City Mall",
      "latitude": "41.299500",
      "longitude": "69.240100"
    }
  }
]
```

---

## Event Detail

```http
GET /api/events/{id}/
```

**Permission:** Ochiq

Bitta event to'liq ma'lumoti. `created_at` ham qaytadi.

---

## Qidirish

```http
GET /api/events/search/?q=chess
```

**Permission:** Ochiq

Qidirish maydonlari:
- Event title
- Category nomi
- Organizer ismi
- Location nomi va manzili

### Response

```json
[
  { "id": 1, "title": "Chess Championship #1" },
  { "id": 4, "title": "Blitz Chess #4" }
]
```

---

## Event Yaratish

```http
POST /api/events/
```

**Permission:** Faqat organizer (`is_organizer=true`)

### Request (multipart/form-data yoki JSON)

```json
{
  "category": 1,
  "location": 1,
  "title": "Chess Tournament",
  "description": "Monthly chess competition",
  "event_date": "2026-06-15",
  "event_time": "18:00",
  "total_seats": 16,
  "is_draft": false
}
```

Rasm bilan yuklash (`multipart/form-data`):
```
image: <file>
```

### Response `201 Created`

```json
{ "message": "Event created" }
```

---

## Event Yangilash

```http
PUT /api/events/{id}/
PATCH /api/events/{id}/
```

**Permission:** Event organizer yoki admin

Request body event yaratish bilan bir xil (partial update ham ishlaydi).

---

## Event Bekor Qilish

```http
DELETE /api/events/{id}/
```

**Permission:** Event organizer yoki admin

Event o'chirilmaydi — `status` → `cancelled` bo'ladi. Barcha qatnashchilarga Telegram notification yuboriladi.

### Response `200 OK`

```json
{ "message": "Event deleted" }
```

---

## Eventga Qo'shilish

```http
POST /api/events/{id}/join/
```

**Permission:** Autentifikatsiya kerak

### Logic

```
seats_left > 0  → Attendance yaratiladi (status: joined)
seats_left == 0 → WaitingList'ga qo'shiladi
```

### Response `200 OK`

```json
{ "message": "Joined successfully" }
```
yoki
```json
{ "message": "Added to waiting list" }
```

### Xatolar

```json
{ "non_field_errors": ["Cannot join cancelled or completed events."] }
{ "non_field_errors": ["You already joined this event."] }
{ "non_field_errors": ["You are already in the waiting list."] }
```

---

## Eventdan Chiqish

```http
POST /api/events/{id}/leave/
```

**Permission:** Autentifikatsiya kerak

Chiqganda: waiting list'dagi birinchi odam avtomatik qo'shiladi va Telegram notification oladi.

### Response `200 OK`

```json
{ "message": "Left successfully" }
```

---

## Qatnashchilar Ro'yxati

```http
GET /api/events/{id}/participants/
```

**Permission:** Event organizer yoki admin

```json
[
  {
    "id": 3,
    "full_name": "Nilufar Karimova",
    "avatar": "https://...",
    "status": "joined"
  },
  {
    "id": 5,
    "full_name": "Bobur Yusupov",
    "avatar": "",
    "status": "attended"
  }
]
```

---

## Kutish Ro'yxati

```http
GET /api/events/{id}/waiting-list/
```

**Permission:** Event organizer yoki admin

```json
[
  { "id": 1, "user": { "id": 7, "full_name": "Aziz Tursunov" } }
]
```

---

## Davomat Belgilash

```http
POST /api/events/{id}/attendance/{user_id}/
```

**Permission:** Event organizer yoki admin

Event tugagandan so'ng organizer qo'lda belgilaydi. Status `joined` → `attended`.

Belgilananda:
- User'ning `total_attended` oshadi
- Achievement tekshiriladi (10 ta o'yin, 30 ta o'yin)

### Response `200 OK`

```json
{ "message": "User marked as attended" }
```
