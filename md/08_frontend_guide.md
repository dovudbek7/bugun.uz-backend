# Frontend Developer Guide

---

## Tezkor Boshlash

```
Base URL:  http://localhost:8000
Swagger:   http://localhost:8000/api/docs/
```

---

## Auth Headers

```js
const API = 'http://localhost:8000/api'

const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${localStorage.getItem('access')}`
}
```

---

## Sahifalar va API'lar

### 1. Bosh Sahifa (Home)

```
Bugungi eventlar:  GET /api/events/today/
Barcha eventlar:   GET /api/events/
Kategoriyalar:     GET /api/categories/
Leaderboard:       GET /api/leaderboard/
```

### 2. Xarita Sahifasi (Map)

```
GET /api/maps/

← koordinatlar + seats_left bilan keladi
← Har bir pin uchun: name, icon, time, seats_left, location.lat/lon
```

### 3. Event Ro'yxati

```
Barcha:        GET /api/events/
Kategoriya:    GET /api/events/?category={id}
Bugun:         GET /api/events/today/
Search:        GET /api/events/search/?q={text}
Paginate:      GET /api/events/?page=2&page_size=10
```

### 4. Event Detail

```
GET /api/events/{id}/

Qo'shilish:  POST /api/events/{id}/join/
Chiqish:     POST /api/events/{id}/leave/
```

Organizer uchun qo'shimcha:
```
Qatnashchilar:   GET /api/events/{id}/participants/
Kutish ro'yxat:  GET /api/events/{id}/waiting-list/
Davomat:         POST /api/events/{id}/attendance/{user_id}/
```

### 5. Profil Sahifasi

```
Mening profil:    GET /api/profile/me/
Profilni yangilash: PUT /api/profile/me/
Boshqa user:      GET /api/profile/{id}/
Tarix:            GET /api/history/me/
Achievement:      GET /api/achievements/me/
```

### 6. Organizer So'rovi

```
Status:    GET /api/organizer/request/
So'rov:    POST /api/organizer/request/
```

### 7. Qiziqishlar (Onboarding'da)

```
GET /api/interests/
```

### 8. Baho Berish

```
POST /api/ratings/
```

### 9. Report

```
POST /api/reports/
```

---

## Token Yangilash — Axios Interceptor

```js
import axios from 'axios'

const api = axios.create({ baseURL: 'http://localhost:8000/api' })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('access')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => res,
  async err => {
    if (err.response?.status === 401) {
      const refresh = localStorage.getItem('refresh')
      if (!refresh) { /* logout */ return }
      try {
        const { data } = await axios.post('/api/auth/refresh/', { refresh })
        localStorage.setItem('access', data.access)
        localStorage.setItem('refresh', data.refresh)
        err.config.headers.Authorization = `Bearer ${data.access}`
        return api(err.config)
      } catch {
        localStorage.clear()
        // → /start ga yo'naltiring
      }
    }
    return Promise.reject(err)
  }
)
```

---

## Til Tanlash

```js
// Foydalanuvchi tili saqlanadi: user.language
const LANGS = {
  uz_latn: "O'zbek (Lotin)",
  uz_cyrl: "O'zbek (Kiril)",
  ru: "Русский",
  en: "English"
}

// API'ga lang yuborish
const { data } = await api.get('/categories/', {
  params: { lang: user.language }
})

// Yoki profil orqali til o'zgartirish
await api.put('/profile/me/', { language: 'ru' })
```

---

## Avatar Fallback

```jsx
// Avatar yo'q bo'lganda birinchi harf
{user.avatar
  ? <img src={user.avatar} alt={user.full_name} />
  : <div className="avatar-placeholder">
      {(user.full_name || user.telegram_username || '?')[0].toUpperCase()}
    </div>
}
```

---

## `seats_left` va Join Tugmasi

```js
// Event card'da
const isFull = event.seats_left === 0
const buttonText = isFull ? 'Kutish ro\'yxati' : 'Qo\'shilish'

// Join so'rovi
const joinEvent = async (eventId) => {
  const { data } = await api.post(`/events/${eventId}/join/`)
  // data.message:
  // "Joined successfully" → qo'shildi
  // "Added to waiting list" → kutish ro'yxatiga
}
```

---

## Event Status Ranglar

```js
const STATUS_COLORS = {
  upcoming: '#10b981',   // yashil
  completed: '#6b7280',  // kulrang
  cancelled: '#ef4444'   // qizil
}

const STATUS_LABELS = {
  uz_latn: {
    upcoming: 'Kelayotgan',
    completed: 'Tugagan',
    cancelled: 'Bekor qilingan'
  },
  ru: {
    upcoming: 'Предстоящий',
    completed: 'Завершён',
    cancelled: 'Отменён'
  }
}
```

---

## Organizer Check

```js
// Event yaratish tugmasini ko'rsatish
{user.is_organizer && <button onClick={openCreateModal}>+ Event</button>}

// Organizer emas bo'lsa
{!user.is_organizer && (
  <button onClick={goToOrganizerRequest}>Organizer bo'lish</button>
)}
```

---

## Leaderboard — Avatar + Rank

```jsx
leaderboard.map((entry, index) => (
  <div key={entry.user.id}>
    <span>#{index + 1}</span>
    <img src={entry.user.avatar} alt="" />
    <span>{entry.user.full_name}</span>
    <span>{entry.total_attended} 🎮</span>
    <span>{entry.rating} ⭐ ({entry.rates_count})</span>
  </div>
))
```

---

## Xatolarni Ko'rsatish

```js
try {
  await api.post('/events/1/join/')
} catch (err) {
  const msg =
    err.response?.data?.non_field_errors?.[0] ||
    err.response?.data?.detail ||
    'Xatolik yuz berdi'
  showToast(msg)
}
```

---

## Muhim Business Qoidalar (Frontend'da tekshirish)

| Holat | Qoida |
|-------|-------|
| `event.status !== 'upcoming'` | Join tugmasi ko'rinmasin |
| `event.is_draft === true` | Ro'yxatda ko'rinmasin |
| `user.is_organizer === false` | Event yarata olmaydi |
| `event.status === 'completed'` | Baho berish tugmasini ko'rsatish |
| `user.show_telegram === false` | Boshqa profilida telegram yashirin |
| `seats_left === 0` | "Kutish ro'yxati"ga qo'shilish |

---

## Fayl Yuklash (Event Image)

```js
const formData = new FormData()
formData.append('title', 'Chess Tournament')
formData.append('category', 1)
formData.append('location', 1)
formData.append('event_date', '2026-06-15')
formData.append('event_time', '18:00')
formData.append('total_seats', 12)
formData.append('is_draft', false)
formData.append('image', fileInput.files[0])  // rasm

await api.post('/events/', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
```

Rasmni ko'rsatish:
```js
// event.image to'liq URL bo'lib keladi
<img src={event.image} alt={event.title} />
```
