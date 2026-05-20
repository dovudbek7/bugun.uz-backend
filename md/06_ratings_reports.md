# Ratings va Reports

---

## Rating System

### Qoidalar

- Faqat `completed` event qatnashchilari bir-birini baholay oladi
- Ikkalasi ham `attended` statusida bo'lishi kerak
- Bir event uchun bir odamni faqat bir marta baholash mumkin
- O'zingizni baholay olmaysiz

---

## Baho Berish

```http
POST /api/ratings/
```

**Permission:** JWT token kerak

### Request Body

```json
{
  "to_user": 5,
  "event_id": 3,
  "stars": 5
}
```

| Field | Type | Required | Izoh |
|-------|------|----------|------|
| `to_user` | integer | ✅ | Baholanayotgan user ID |
| `event_id` | integer | ✅ | Event ID |
| `stars` | integer (1-5) | ✅ | Yulduz soni |

### Response `201 Created`

```json
{ "message": "Rating submitted" }
```

### Xatolar

```json
{ "non_field_errors": ["You cannot rate yourself."] }
{ "non_field_errors": ["Event must be completed before rating."] }
{ "non_field_errors": ["Only attended participants can rate each other."] }
{ "non_field_errors": ["You already rated this user for this event."] }
```

> Baho berilganda — baholanayotgan user'ning `rating` field'i qayta hisoblanadi (average).

---

## Leaderboard

Leaderboard hujjati: [03_profile.md](./03_profile.md#leaderboard)

---

## Report System

### Qoidalar

- Har qanday foydalanuvchini report qilish mumkin (event qatnashishi shart emas)
- O'zingizni report qila olmaysiz
- Hozirda moderation avtomatlashtirilmagan — admin ko'rib chiqadi

---

## Report Yuborish

```http
POST /api/reports/
```

**Permission:** JWT token kerak

### Request Body

```json
{
  "target_user_id": 7,
  "message": "Eventda noto'g'ri xatti-harakat qildi."
}
```

| Field | Type | Required | Izoh |
|-------|------|----------|------|
| `target_user_id` | integer | ✅ | Report qilinayotgan user ID |
| `message` | string | ✅ | Sabab |

### Response `201 Created`

```json
{ "message": "Report submitted" }
```

### Xatolar

```json
{ "non_field_errors": ["You cannot report yourself."] }
```

---

## Admin: Reportlar Ro'yxati (API)

```http
GET /api/admin/reports/
```

**Permission:** Faqat admin

### Response `200 OK`

```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "reporter": { "id": 3, "full_name": "Nilufar Karimova" },
      "target_user": { "id": 7, "full_name": "Aziz Tursunov" },
      "message": "Eventda noto'g'ri xatti-harakat qildi.",
      "created_at": "2026-05-15T14:30:00Z"
    }
  ]
}
```

---

## Admin: Reportlar Sahifasi (HTML)

```
GET /dashboard/reports/
```

Faqat admin. Chiroyli karta ko'rinishida barcha reportlar.

---

## Frontend uchun Eslatmalar

### Baho berish qachon ko'rsatiladi

```js
// Event detail sahifasida faqat shu shartlarda ko'rsating:
const canRate = (
  event.status === 'completed' &&
  currentUser.status === 'attended' &&  // attendance'dan
  !alreadyRated
)
```

### Report tugmasi

Har qanday user profilida ko'rsatish mumkin (o'zingizdaniki emas):

```js
if (profileUser.id !== currentUser.id) {
  // "Report" tugmasini ko'rsating
}
```
