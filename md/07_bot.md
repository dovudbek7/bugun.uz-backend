# Telegram Bot

---

## Bot Token

```
8980123227:AAGkb2zjBGBiUCd9jzVQAKDVzVk9J8InGR8
```

Bu test token. Production'da `.env` ga yoziladi.

---

## Bot Ishga Tushirish

```bash
python -m apps.telegram_bot.run
```

Docker bilan — avtomatik ishga tushadi.

---

## /start — Ro'yxatdan O'tish

**Oqim:**

```
1. Foydalanuvchi /start bosadi
2. Bot til tanlash klaviaturasi ko'rsatadi:
   🇺🇿 O'zbek (Lotin)  |  🇺🇿 O'zbek (Kiril)
   🇷🇺 Ruscha           |  🇬🇧 Inglizcha
3. Til tanlanadi → DBga saqlanadi
4. Bot tanlangan tilda xush kelibsiz + telefon so'raydi
5. Foydalanuvchi telefon ulashadi
6. Telefon DBga saqlanadi
7. Avatar Telegramdan avtomatik olinadi
8. Mini App tugmasi ko'rsatiladi (URL sozlangan bo'lsa)
```

**Qaytib kelgan foydalanuvchi:** Telefoni bor bo'lsa — til tanlash o'tkazib yuboriladi, xush kelibsiz xabari ko'rsatiladi.

---

## /profile

Foydalanuvchining o'z tilidagi profil ma'lumotlari:

```
👤 Profil

Ism: Dovudbek Xabibullayev
Reyting: 4.8 ⭐
Jami o'yinlar: 15
Organizer: ✅ Ha
Viloyat: Tashkent
Telefon: +998901234567
Telegram: @dovudbek_x
```

---

## /games

Qo'shilgan eventlar ro'yxati:

```
🎮 O'yinlaringiz

🟢 Kelayotgan
• Chess Championship #3 — 2026-05-20
• Mafia Night #5 — 2026-05-22

✅ Tugatilgan
• Chess Tournament #1 — 2026-05-10
• Board Games Friday #2 — 2026-05-12
```

---

## /location

Joylashuvni ulashish oqimi:

```
1. /location buyrug'i → Joylashuv tugmasi chiqadi
2. Foydalanuvchi tugmani bosadi → Telegram location yuboradi
3. Koordinatlar DBga saqlanadi (user.last_latitude, user.last_longitude)
4. Tasdiqlash xabari yuboriladi
```

---

## /help

Barcha buyruqlar va qisqa yo'riqnoma tanlangan tilda.

---

## Til Tizimi

Bot tanlangan tilni DBga saqlaydi. Keyingi barcha xabarlar o'sha tilda.

| Til Kodi | Til |
|----------|-----|
| `uz_latn` | O'zbek lotin |
| `uz_cyrl` | O'zbek kiril (lotin'dan auto-konvert) |
| `ru` | Ruscha |
| `en` | Inglizcha |

**Kiril konversiyasi:** Lotin matnlar `latin_to_cyrillic()` orqali avtomatik o'tkaziladi. Alohida kiril lug'at saqlanmaydi.

---

## Telegram Notifications (Celery)

Barcha bildirishnomalar `send_event_notification` Celery task orqali yuboriladi.

### Organizer Tasdiqlandi

```
✅ Your organizer request has been approved.
```

Qachon: Admin tasdiqlanganda (`POST /api/admin/organizer-requests/{id}/approve/`)

---

### Waiting List'dan O'tish

```
You were moved from waiting list to joined for Chess Championship #1.
```

Qachon: Kimdir eventdan chiqqanda, birinchi waiting user avtomatik qo'shiladi.

---

### Event Reminder (24 soat oldin)

```
Reminder: Chess Championship #1 starts on 2026-05-20 at 18:00:00.
```

Qachon: Celery Beat har 15 daqiqada tekshiradi.

---

### Event Bekor Qilindi

```
Event cancelled: Chess Championship #1.
```

Qachon: Organizer eventni `DELETE /api/events/{id}/` qilganda.

---

## Mini App Tugmasi

`.env` da `MINI_APP_URL` haqiqiy URL bo'lsa — inline WebApp tugmasi ko'rsatiladi:

```env
MINI_APP_URL=https://your-mini-app.com
```

Agar URL sozlanmagan bo'lsa — tugma ko'rinmaydi (xato chiqarmaydi).

---

## Avatar Olish

Bot `/start` paytida Telegram API'dan fotosuratni avtomatik oladi:

```python
photos = await bot.get_user_profile_photos(user_id, limit=1)
# → fayl URL sifatida saqlaydi
```

Avatar yo'q bo'lsa — bo'sh qoladi. Frontend birinchi harfni ko'rsatadi.
