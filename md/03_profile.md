# Profile, History, Leaderboard, Achievements

---

## Mening Profilim

```http
GET /api/profile/me/
```

**Permission:** JWT token kerak

### Response `200 OK`

```json
{
  "id": 1,
  "full_name": "Dovudbek Xabibullayev",
  "telegram_username": "dovudbek_x",
  "avatar": "https://api.telegram.org/file/bot.../photos/...",
  "age": 22,
  "region": "Tashkent",
  "phone_number": "+998901234567",
  "language": "uz_latn",
  "show_telegram": true,
  "is_organizer": false,
  "total_attended": 15,
  "rating": "4.80",
  "interests": [
    { "id": 1, "title": "Shaxmat", "title_ru": "Шахматы", "title_en": "Chess", "icon": "♟️" }
  ],
  "achievements": [
    { "id": 1, "title": "10 Events Joined", "icon": "🏆", "description": "Joined 10 events" }
  ],
  "history": [
    {
      "event": { "id": 3, "title": "Chess Championship" },
      "status": "attended",
      "date": "2026-05-10"
    }
  ]
}
```

---

## Profilni Yangilash

```http
PUT /api/profile/me/
```

**Permission:** JWT token kerak

### Request Body

```json
{
  "full_name": "Dovudbek Xabibullayev",
  "age": 22,
  "region": "Tashkent",
  "phone_number": "+998901234567",
  "show_telegram": true,
  "language": "uz_latn",
  "interests": [1, 2, 3]
}
```

Barcha fieldlar optional (partial update).

> `interests` yuborilsa — eski qiziqishlar o'chiriladi, yangisi yoziladi.

### Response `200 OK`

```json
{ "message": "Profile updated" }
```

---

## Boshqa Foydalanuvchi Profili

```http
GET /api/profile/{id}/
```

**Permission:** JWT token kerak

Agar `show_telegram=false` bo'lsa — `telegram_username` null qaytadi.
`phone_number` faqat o'z profilingizda ko'rinadi.

---

## O'yin Tarixi

```http
GET /api/history/me/
```

**Permission:** JWT token kerak

Pagination yo'q. Oxirgi eventlar boshida keladi.

### Response `200 OK`

```json
[
  {
    "event": { "id": 5, "title": "Mafia Night #2" },
    "status": "attended",
    "date": "2026-05-12"
  },
  {
    "event": { "id": 3, "title": "Chess Championship" },
    "status": "joined",
    "date": "2026-05-20"
  }
]
```

### Attendance Status Qiymatlari

| Status | Ma'no |
|--------|-------|
| `joined` | Qo'shilgan (hali bo'lmagan) |
| `attended` | Qatnashgan (organizer belgilagan) |
| `cancelled` | Chiqib ketgan |

---

## Mening Achievementlarim

```http
GET /api/achievements/me/
```

**Permission:** JWT token kerak

Pagination yo'q.

### Response `200 OK`

```json
[
  {
    "id": 1,
    "title": "10 Events Joined",
    "icon": "🏆",
    "description": "Joined 10 events"
  },
  {
    "id": 2,
    "title": "Top Organizer",
    "icon": "👑",
    "description": "Recognized as a top event organizer"
  }
]
```

### Achievement'lar Qachon Beriladi

| Achievement | Shart |
|------------|-------|
| 10 Events Joined | `total_attended >= 10` |
| 30 Games Played | `total_attended >= 30` |
| Top Organizer | Admin tomonidan qo'lda |

---

## Leaderboard

```http
GET /api/leaderboard/
```

**Permission:** Ochiq

Top 100 foydalanuvchi. Pagination yo'q. Tartiblash: `total_attended` ↓, `rating` ↓.

### Response `200 OK`

```json
[
  {
    "user": {
      "id": 1,
      "full_name": "Dovudbek Xabibullayev",
      "avatar": "https://..."
    },
    "total_attended": 25,
    "rating": "4.90",
    "rates_count": 48
  },
  ...
]
```

| Field | Izoh |
|-------|------|
| `total_attended` | Qatnashgan eventlar soni |
| `rating` | O'rtacha yulduz (1-5) |
| `rates_count` | Nechta baho olgan |
