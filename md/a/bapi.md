# EVENT COMMUNITY PLATFORM API DOCUMENTATION

## Django REST Framework Backend API

Base URL:

```http
/api/
```

Authentication:

```http
Authorization: Bearer <token>
```

---

# AUTH APIs

---

# 1. TELEGRAM LOGIN

## Endpoint

```http
POST /api/auth/telegram/
```

---

## Description

Telegram bot orqali user authentication.

Telegram start bosilganda:

- telegram_id
- username
- avatar

backendga yuboriladi.

---

## Request

```json
{
  "telegram_id": 123456789,
  "telegram_username": "dovudbek",
  "avatar": "image_url",
  "language": "uz_latn"
}
```

---

## Response

```json
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": {
    "id": 1,
    "full_name": null,
    "is_organizer": false
  }
}
```

---

# 2. COMPLETE PROFILE

## Endpoint

```http
POST /api/auth/onboarding/
```

---

## Description

Mini app onboarding.

---

## Request

```json
{
  "full_name": "Dovudbek",
  "age": 21,
  "region": "Tashkent",
  "phone_number": "+998901234567",
  "show_telegram": true,
  "interests": [1, 2, 3]
}
```

---

## Response

```json
{
  "message": "Profile completed"
}
```

---

# 3. REFRESH TOKEN

## Endpoint

```http
POST /api/auth/refresh/
```

---

## Request

```json
{
  "refresh": "refresh_token"
}
```

---

## Response

```json
{
  "access": "new_access_token"
}
```

---

# PROFILE APIs

---

# 4. MY PROFILE

## Endpoint

```http
GET /api/profile/me/
```

---

## Response

```json
{
  "id": 1,
  "full_name": "Dovudbek",
  "telegram_username": "dovudbek",
  "avatar": "image",
  "age": 21,
  "region": "Tashkent",
  "phone_number": "+998901234567",
  "language": "uz_latn",
  "show_telegram": true,
  "is_organizer": false,
  "total_attended": 15,
  "rating": 4.8,
  "interests": [
    {
      "id": 1,
      "title": "Chess",
      "icon": "icon"
    }
  ],
  "achievements": [],
  "history": []
}
```

---

# 5. UPDATE PROFILE

## Endpoint

```http
PUT /api/profile/me/
```

---

## Request

```json
{
  "full_name": "Dovudbek",
  "age": 22,
  "region": "Samarkand",
  "phone_number": "+998901234567",
  "show_telegram": false,
  "language": "uz_latn",
  "interests": [1, 2]
}
```

---

## Response

```json
{
  "message": "Profile updated"
}
```

---

# 6. GET USER PROFILE

## Endpoint

```http
GET /api/profile/:id/
```

---

## Response

```json
{
  "id": 5,
  "full_name": "Ali",
  "avatar": "image",
  "age": 20,
  "region": "Tashkent",
  "language": "uz_latn",
  "show_telegram": true,
  "telegram_username": "ali_user",
  "total_attended": 12,
  "rating": 4.5,
  "interests": [],
  "achievements": [],
  "history": []
}
```

---

# CATEGORY APIs

---

# 7. GET CATEGORIES

## Endpoint

```http
GET /api/categories/
```

---

## Response

```json
[
  {
    "id": 1,
    "title": "Chess",
    "icon": "icon",
    "color": "#000"
  }
]
```

---

# INTEREST APIs

---

# 8. GET INTERESTS

## Endpoint

```http
GET /api/interests/
```

---

## Response

```json
[
  {
    "id": 1,
    "title": "Chess",
    "icon": "icon"
  }
]
```

---

# LOCATION APIs

---

# 9. GET LOCATIONS

## Endpoint

```http
GET /api/locations/
```

---

## Response

```json
[
  {
    "id": 1,
    "title": "Magic City",
    "latitude": "41.31",
    "longitude": "69.24",
    "address": "Tashkent"
  }
]
```

---

# 10. CREATE LOCATION

## Endpoint

```http
POST /api/locations/
```

---

## Description

Organizer yangi location create qila oladi.

---

## Request

```json
{
  "title": "Magic City",
  "latitude": "41.31",
  "longitude": "69.24",
  "address": "Tashkent"
}
```

---

## Response

```json
{
  "message": "Location created"
}
```

---

# EVENT APIs

---

# 11. GET EVENTS

## Endpoint

```http
GET /api/events/
```

---

## Query Params

```http
?category=1
?today=true
?status=upcoming
?draft=false
?page=1
```

---

## Response

```json
[
  {
    "id": 1,
    "title": "Chess Tournament",
    "description": "Weekend games",
    "category": {
      "id": 1,
      "title": "Chess",
      "icon": "icon"
    },
    "location": {
      "id": 1,
      "title": "Magic City"
    },
    "event_date": "2026-05-20",
    "event_time": "18:00",
    "total_seats": 20,
    "seats_left": 5,
    "status": "upcoming",
    "participants": [
      {
        "id": 1,
        "avatar": "image"
      }
    ],
    "organizer": {
      "id": 1,
      "full_name": "Dovudbek"
    }
  }
]
```

---

# 12. GET TODAY EVENTS

## Endpoint

```http
GET /api/events/?today=true
```

---

## Description

Main page uchun faqat bugungi eventlar.

---

# 13. GET SINGLE EVENT

## Endpoint

```http
GET /api/events/:id/
```

---

## Response

```json
{
  "id": 1,
  "title": "Chess Tournament",
  "description": "Weekend chess games",
  "category": {},
  "location": {},
  "event_date": "2026-05-20",
  "event_time": "18:00",
  "total_seats": 20,
  "seats_left": 5,
  "status": "upcoming",
  "participants": [],
  "organizer": {},
  "created_at": "2026-05-10"
}
```

---

# 14. CREATE EVENT

## Endpoint

```http
POST /api/events/
```

---

## Permission

```python
is_organizer=True
```

---

## Request

```json
{
  "category": 1,
  "location": 1,
  "title": "Chess Meetup",
  "description": "Weekend chess games",
  "event_date": "2026-05-20",
  "event_time": "18:00",
  "total_seats": 20,
  "is_draft": false
}
```

---

## Response

```json
{
  "message": "Event created"
}
```

---

# 15. UPDATE EVENT

## Endpoint

```http
PUT /api/events/:id/
```

---

## Request

```json
{
  "title": "Updated Chess Meetup",
  "description": "Updated description",
  "total_seats": 25
}
```

---

## Response

```json
{
  "message": "Event updated"
}
```

---

# 16. DELETE EVENT

## Endpoint

```http
DELETE /api/events/:id/
```

---

## Response

```json
{
  "message": "Event deleted"
}
```

---

# 17. SEARCH EVENTS

## Endpoint

```http
GET /api/events/search/?q=chess
```

---

## Search Fields

- title
- category
- organizer
- location

---

## Response

```json
[
  {
    "id": 1,
    "title": "Chess Tournament"
  }
]
```

---

# ATTENDANCE APIs

---

# 18. JOIN EVENT

## Endpoint

```http
POST /api/events/:id/join/
```

---

## Logic

If seats available:

```python
Attendance create
```

Else:

```python
WaitingList create
```

---

## Response

### Joined

```json
{
  "message": "Joined successfully"
}
```

---

### Waiting List

```json
{
  "message": "Added to waiting list"
}
```

---

# 19. LEAVE EVENT

## Endpoint

```http
POST /api/events/:id/leave/
```

---

## Response

```json
{
  "message": "Left successfully"
}
```

---

# 20. GET EVENT PARTICIPANTS

## Endpoint

```http
GET /api/events/:id/participants/
```

---

## Response

```json
[
  {
    "id": 1,
    "full_name": "Ali",
    "avatar": "image",
    "status": "joined"
  }
]
```

---

# 21. MARK USER AS ATTENDED

## Endpoint

```http
POST /api/events/:id/attendance/:user_id/
```

---

## Permission

Faqat organizer.

---

## Response

```json
{
  "message": "User marked as attended"
}
```

---

# WAITING LIST APIs

---

# 22. GET WAITING LIST

## Endpoint

```http
GET /api/events/:id/waiting-list/
```

---

## Permission

Faqat organizer.

---

## Response

```json
[
  {
    "id": 1,
    "user": {
      "id": 5,
      "full_name": "Ali"
    }
  }
]
```

---

# RATING APIs

---

# 23. RATE USER

## Endpoint

```http
POST /api/ratings/
```

---

## Request

```json
{
  "to_user": 5,
  "event_id": 1,
  "stars": 5
}
```

---

## Response

```json
{
  "message": "Rating submitted"
}
```

---

# LEADERBOARD APIs

---

# 24. GET LEADERBOARD

## Endpoint

```http
GET /api/leaderboard/
```

---

## Response

```json
[
  {
    "user": {
      "id": 1,
      "full_name": "Dovudbek",
      "avatar": "image"
    },
    "total_attended": 25,
    "rating": 4.9,
    "rates_count": 50
  }
]
```

---

# ORGANIZER APIs

---

# 25. SEND ORGANIZER REQUEST

## Endpoint

```http
POST /api/organizer/request/
```

---

## Request

```json
{
  "message": "I want to organize chess events"
}
```

---

## Response

```json
{
  "message": "Request sent"
}
```

---

# 26. GET MY ORGANIZER REQUEST

## Endpoint

```http
GET /api/organizer/request/
```

---

## Response

```json
{
  "status": "pending"
}
```

---

# REPORT APIs

---

# 27. SEND REPORT

## Endpoint

```http
POST /api/reports/
```

---

## Request

```json
{
  "target_user_id": 5,
  "message": "Spam behavior"
}
```

---

## Response

```json
{
  "message": "Report submitted"
}
```

---

# ACHIEVEMENT APIs

---

# 28. GET MY ACHIEVEMENTS

## Endpoint

```http
GET /api/achievements/me/
```

---

## Response

```json
[
  {
    "id": 1,
    "title": "10 Events Joined",
    "icon": "icon",
    "description": "Joined 10 events"
  }
]
```

---

# HISTORY APIs

---

# 29. GET MY HISTORY

## Endpoint

```http
GET /api/history/me/
```

---

## Response

```json
[
  {
    "event": {
      "id": 1,
      "title": "Chess Tournament"
    },
    "status": "attended",
    "date": "2026-05-20"
  }
]
```

---

# ADMIN APIs

---

# 30. GET ORGANIZER REQUESTS

## Endpoint

```http
GET /api/admin/organizer-requests/
```

---

# 31. APPROVE ORGANIZER

## Endpoint

```http
POST /api/admin/organizer-requests/:id/approve/
```

---

# 32. REJECT ORGANIZER

## Endpoint

```http
POST /api/admin/organizer-requests/:id/reject/
```

---

# 33. GET REPORTS

## Endpoint

```http
GET /api/admin/reports/
```

---

# TELEGRAM BOT NOTIFICATIONS

---

# Notifications Sent Through Bot

- Event reminder
- Event cancelled
- Waiting list approved
- Organizer approved
- Organizer rejected

---

# BUSINESS RULES

---

# Event Rules

- Only organizers can create events
- Draft events publicda ko‘rinmaydi
- Event full bo‘lsa waiting list ishlaydi

---

# Attendance Rules

- One user -> one attendance
- Organizer attended status qo‘yadi

---

# Rating Rules

- Only participants can rate
- Event completed bo‘lishi kerak

---

# Organizer Rules

- Organizer request required
- Admin approval required

---

# SECURITY RULES

---

# Authentication

Telegram verification required.

---

# Permissions

```python
Normal User:
- join event
- leave event
- report users
- rate users

Organizer:
- create event
- update event
- manage attendance

Admin:
- approve organizers
- view reports
```

---

# RECOMMENDED STACK

```python
Backend:
- Django
- DRF

Database:
- PostgreSQL

Authentication:
- JWT

Async Tasks:
- Celery

Cache:
- Redis

Deployment:
- Docker
- Nginx
- Gunicorn
```

---

# PERFORMANCE NOTES

Use:

- select_related
- prefetch_related
- pagination
- indexing
