# Endpoints — Quick Reference

Barcha endpointlar jadval ko'rinishida.

---

## Auth

| Method | URL | Auth | Izoh |
|--------|-----|------|------|
| POST | `/api/auth/telegram/` | ❌ | Telegram login → JWT |
| POST | `/api/auth/onboarding/` | ✅ | Profil to'ldirish |
| POST | `/api/auth/refresh/` | ❌ | Token yangilash |

---

## Events

| Method | URL | Auth | Kim |
|--------|-----|------|-----|
| GET | `/api/events/` | ❌ | Barcha eventlar |
| POST | `/api/events/` | ✅ | Organizer |
| GET | `/api/events/{id}/` | ❌ | Event detail |
| PUT/PATCH | `/api/events/{id}/` | ✅ | Organizer/Admin |
| DELETE | `/api/events/{id}/` | ✅ | Organizer/Admin |
| GET | `/api/events/today/` | ❌ | Bugungi eventlar |
| GET | `/api/events/search/?q=` | ❌ | Qidirish |
| POST | `/api/events/{id}/join/` | ✅ | Har kim |
| POST | `/api/events/{id}/leave/` | ✅ | Har kim |
| GET | `/api/events/{id}/participants/` | ✅ | Organizer/Admin |
| GET | `/api/events/{id}/waiting-list/` | ✅ | Organizer/Admin |
| POST | `/api/events/{id}/attendance/{user_id}/` | ✅ | Organizer/Admin |

---

## Maps

| Method | URL | Auth | Izoh |
|--------|-----|------|------|
| GET | `/api/maps/` | ❌ | Koordinatli upcoming eventlar |

---

## Profile

| Method | URL | Auth | Izoh |
|--------|-----|------|------|
| GET | `/api/profile/me/` | ✅ | Mening profilim |
| PUT | `/api/profile/me/` | ✅ | Profilni yangilash |
| GET | `/api/profile/{id}/` | ✅ | Boshqa user profili |
| GET | `/api/history/me/` | ✅ | Event tarixi |
| GET | `/api/achievements/me/` | ✅ | Achievement'lar |
| GET | `/api/leaderboard/` | ❌ | Top foydalanuvchilar |

---

## Categories, Interests, Locations

| Method | URL | Auth | Izoh |
|--------|-----|------|------|
| GET | `/api/categories/` | ❌ | Kategoriyalar |
| GET | `/api/interests/` | ❌ | Qiziqishlar |
| GET | `/api/locations/` | ❌ | Manzillar |
| POST | `/api/locations/` | ✅ | Yangi manzil (organizer) |

---

## Organizer

| Method | URL | Auth | Kim |
|--------|-----|------|-----|
| GET | `/api/organizer/request/` | ✅ | Har kim |
| POST | `/api/organizer/request/` | ✅ | Har kim |
| GET | `/api/admin/organizer-requests/` | ✅ | Admin |
| POST | `/api/admin/organizer-requests/{id}/approve/` | ✅ | Admin |
| POST | `/api/admin/organizer-requests/{id}/reject/` | ✅ | Admin |

---

## Ratings & Reports

| Method | URL | Auth | Izoh |
|--------|-----|------|------|
| POST | `/api/ratings/` | ✅ | Baho berish |
| POST | `/api/reports/` | ✅ | Report yuborish |
| GET | `/api/admin/reports/` | ✅ | Admin — reportlar |

---

## Docs & Dashboard

| Method | URL | Auth | Izoh |
|--------|-----|------|------|
| GET | `/api/docs/` | ❌ | Swagger UI |
| GET | `/api/schema/` | ❌ | OpenAPI JSON |
| GET | `/admin/` | ✅ | Django admin |
| GET | `/dashboard/statistics/` | ✅ | Custom statistika |
| GET | `/dashboard/reports/` | ✅ | Reportlar HTML |

---

## Query Params (Umumiy)

| Param | Ishlatiladigan joy | Misol |
|-------|--------------------|-------|
| `page` | Ko'p sahifali endpoint'lar | `?page=2` |
| `page_size` | Ko'p sahifali endpoint'lar | `?page_size=10` |
| `lang` | categories, interests | `?lang=ru` |
| `category` | `/api/events/` | `?category=1` |
| `status` | `/api/events/` | `?status=upcoming` |
| `today` | `/api/events/` | `?today=true` |
| `q` | `/api/events/search/` | `?q=chess` |
