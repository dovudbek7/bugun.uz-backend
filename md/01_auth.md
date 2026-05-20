# Authentication

Ikki bosqichli auth:
1. **Telegram Bot** — telegram_id, phone, avatar bilan ro'yxatdan o'tish → JWT olish
2. **Mini App Onboarding** — ism, yosh, hudud, qiziqishlarni to'ldirish

---

## Step 1 — Telegram Login

```http
POST /api/auth/telegram/
```

**Permission:** Ochiq (token shart emas)

### Request Body

```json
{
  "telegram_id": 123456789,
  "telegram_username": "dovudbek_x",
  "avatar": "https://...",
  "language": "uz_latn",
  "phone_number": "+998901234567"
}
```

| Field | Type | Required | Izoh |
|-------|------|----------|------|
| `telegram_id` | integer | ✅ | Telegram user ID |
| `telegram_username` | string | ❌ | `@username` (@ siz) |
| `avatar` | string (URL) | ❌ | Telegram profile photo URL |
| `language` | string | ❌ | `uz_latn` / `uz_cyrl` / `ru` / `en` |
| `phone_number` | string | ❌ | Bot orqali olingan raqam |

### Response `200 OK`

```json
{
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "full_name": null,
    "is_organizer": false
  }
}
```

> **Muhim:** Foydalanuvchi mavjud bo'lsa update qiladi, yangi bo'lsa yaratadi.

---

## Step 2 — Onboarding (Mini App)

```http
POST /api/auth/onboarding/
```

**Permission:** JWT token kerak (`Authorization: Bearer <access>`)

### Request Body

```json
{
  "full_name": "Dovudbek Xabibullayev",
  "age": 22,
  "region": "Tashkent",
  "phone_number": "+998901234567",
  "show_telegram": true,
  "interests": [1, 2, 3]
}
```

| Field | Type | Required | Izoh |
|-------|------|----------|------|
| `full_name` | string | ❌ | To'liq ism |
| `age` | integer | ❌ | Yosh |
| `region` | string | ❌ | Shahar/viloyat |
| `phone_number` | string | ❌ | Telefon raqam |
| `show_telegram` | boolean | ❌ | Telegram username boshqalarga ko'rinsinmi |
| `interests` | array[int] | ❌ | Interest ID'lar ro'yxati |

### Response `200 OK`

```json
{ "message": "Profile completed" }
```

---

## Token Refresh

```http
POST /api/auth/refresh/
```

**Permission:** Ochiq

### Request Body

```json
{ "refresh": "eyJhbGciOiJIUzI1NiIs..." }
```

### Response `200 OK`

```json
{
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

> `ROTATE_REFRESH_TOKENS=True` — har refresh'da yangi `refresh` token ham qaytadi.

---

## Frontend Auth Flow

```
Bot /start
  → telegram_id, username, avatar olinadi
  → POST /api/auth/telegram/ → access + refresh token
  → localStorage'ga saqlang

Mini App ochiladi
  → token bor → onboarding to'ldirilganmi? tekshiring
  → full_name == null → onboarding sahifasiga yo'naltiring
  → onboarding tugallangan → bosh sahifaga

Token muddati o'tganda
  → POST /api/auth/refresh/ → yangi access oling
  → 401 xatolik → foydalanuvchini /start ga yuborish
```

---

## Token Storage (tavsiya)

```js
// Saqlash
localStorage.setItem('access', data.access)
localStorage.setItem('refresh', data.refresh)

// Har request'ga qo'shish
headers: {
  'Authorization': `Bearer ${localStorage.getItem('access')}`
}
```
