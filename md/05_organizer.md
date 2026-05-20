# Organizer System

---

## Umumiy Mantiq

Har bir foydalanuvchi event yarata olmaydi.

```
User → Organizer so'rovi yuboradi
Admin → So'rovni ko'rib chiqadi
Admin → Tasdiqlaydi / Rad etadi
Tasdiqlansa → user.is_organizer = true
User → Endi event yarata oladi
```

Tasdiqlananda foydalanuvchiga Telegram notification keladi.

---

## Organizer So'rovini Ko'rish

```http
GET /api/organizer/request/
```

**Permission:** JWT token kerak

### Response `200 OK`

```json
{ "status": "pending" }
```

yoki so'rov yuborilmagan bo'lsa:

```json
{ "status": null }
```

### Status Qiymatlari

| Qiymat | Ma'no |
|--------|-------|
| `null` | Hali so'rov yuborilmagan |
| `pending` | Ko'rib chiqilmoqda |
| `approved` | Tasdiqlandi |
| `rejected` | Rad etildi |

---

## Organizer So'rovi Yuborish

```http
POST /api/organizer/request/
```

**Permission:** JWT token kerak

### Request Body

```json
{
  "message": "Toshkentda chess eventlarini organize qilmoqchiman."
}
```

### Response `201 Created`

```json
{ "message": "Request sent" }
```

---

## Admin: So'rovlar Ro'yxati

```http
GET /api/admin/organizer-requests/
```

**Permission:** Faqat admin (`is_staff=true`)

### Response `200 OK`

```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 12,
        "full_name": "Firdavs Qodirov",
        "telegram_username": "firdavs_q"
      },
      "message": "Chess eventlarini organize qilmoqchiman.",
      "status": "pending",
      "created_at": "2026-05-15T10:30:00Z"
    }
  ]
}
```

---

## Admin: So'rovni Tasdiqlash

```http
POST /api/admin/organizer-requests/{id}/approve/
```

**Permission:** Faqat admin

- `application.status` → `approved`
- `user.is_organizer` → `true`
- Telegram notification yuboriladi

### Response `200 OK`

```json
{ "message": "Organizer approved" }
```

---

## Admin: So'rovni Rad Etish

```http
POST /api/admin/organizer-requests/{id}/reject/
```

**Permission:** Faqat admin

- `application.status` → `rejected`
- Telegram notification yuboriladi

### Response `200 OK`

```json
{ "message": "Organizer rejected" }
```

---

## Frontend uchun Organizer Flow

### Foydalanuvchi tomonidan

```
Profile sahifasida "Organizer bo'lish" tugmasi
  → GET /api/organizer/request/ → status tekshirish
  → null: Forma ko'rsating (message yozing)
    → POST /api/organizer/request/
  → pending: "Ko'rib chiqilmoqda" xabari
  → approved: Event yaratish mumkin
  → rejected: Qayta so'rov yuborish imkoniyati
```

### Event yaratish tugmasi

```js
if (user.is_organizer) {
  // Event yaratish formasini ko'rsating
} else {
  // "Organizer bo'ling" sahifasiga yo'naltiring
}
```
