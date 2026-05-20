# EVENT COMMUNITY PLATFORM
# Backend Architecture Documentation
## Stack: Django + DRF + PostgreSQL + Telegram Mini App

---

# PROJECT OVERVIEW

Bu platforma community-based event system hisoblanadi.

Platformada userlar:
- eventlarga qo‘shila oladi
- organizer bo‘la oladi
- event create qila oladi
- boshqa userlarni rating qila oladi
- leaderboardda qatnashadi

Platforma asosan:
- chess
- mafia
- board games
- meetup
- offline community eventlar

uchun ishlatiladi.

---

# SUPPORTED LANGUAGES

```python
LANGUAGES = [
    "uz_latn",
    "uz_cyrl",
    "ru",
    "en"
]
```

---

# MAIN APPS STRUCTURE

```bash
apps/
│
├── accounts/
├── events/
├── attendance/
├── categories/
├── interests/
├── locations/
├── ratings/
├── organizer/
├── reports/
└── common/
```

---

# DATABASE MODELS

---

# USER MODEL

```python
User
- id
- telegram_id
- telegram_username
- full_name
- avatar
- age
- region
- phone_number
- language
- show_telegram
- is_organizer
- total_attended
- rating
- created_at
- updated_at
```

---

# FIELD DESCRIPTIONS

## telegram_id

Telegram user unique id.

Unique bo‘lishi kerak.

---

## telegram_username

Optional field.

Usernameli userlar uchun.

---

## avatar

Telegram profile image.

Optional.

Agar image bo‘lmasa frontend:
- first letter
chiqaradi.

---

## language

```python
choices = [
    "uz_latn",
    "uz_cyrl",
    "ru",
    "en"
]
```

Default:
```python
uz_latn
```

---

## show_telegram

```python
True -> boshqa userlar telegramiga yozishi mumkin
False -> yashirin
```

---

## is_organizer

```python
False -> normal user
True -> organizer access mavjud
```

---

## total_attended

User qatnashgan total eventlar soni.

Attendance orqali calculate qilinadi.

---

## rating

Average rating.

---

# INTEREST MODEL

```python
Interest
- id
- title
- icon
```

---

# NOTES

Admin panel orqali yaratiladi.

Examples:
- Chess
- Mafia
- Board Games
- Football

---

# USER INTEREST MODEL

```python
UserInterest
- id
- user_id
- interest_id
```

---

# NOTES

ManyToMany relation.

User bir nechta interest tanlay oladi.

---

# CATEGORY MODEL

```python
Category
- id
- title
- icon
- color
```

---

# NOTES

Event type/category.

Examples:
- Chess
- Mafia
- Meetup
- Tournament

---

# LOCATION MODEL

```python
Location
- id
- title
- latitude
- longitude
- address
- created_at
```

---

# NOTES

Map uchun ishlatiladi.

Bir locationda bir nechta event bo‘lishi mumkin.

---

# EVENT MODEL

```python
Event
- id
- organizer_id
- category_id
- location_id
- title
- description
- event_date
- event_time
- total_seats
- status
- is_draft
- created_at
- updated_at
```

---

# EVENT STATUS

```python
choices = [
    "upcoming",
    "completed",
    "cancelled"
]
```

---

# NOTES

## organizer_id

User model bilan relation.

---

## total_seats

Maximum participant count.

---

## seats_left

Database field EMAS.

Runtime calculate qilinadi.

Formula:

```python
seats_left = total_seats - joined_users
```

---

## is_draft

```python
True -> publish qilinmagan
False -> public event
```

---

# ATTENDANCE MODEL

```python
Attendance
- id
- user_id
- event_id
- status
- joined_at
```

---

# ATTENDANCE STATUS

```python
choices = [
    "joined",
    "attended",
    "cancelled"
]
```

---

# NOTES

## joined

Eventga yozilgan.

---

## attended

Organizer dashboarddan:
"keldi"
qilib belgilaydi.

---

## cancelled

User leave qilgan.

---

# UNIQUE CONSTRAINT

```python
(user_id, event_id)
```

Bir user bitta eventga faqat bir marta join qila oladi.

---

# WAITING LIST MODEL

```python
WaitingList
- id
- user_id
- event_id
- created_at
```

---

# LOGIC

Agar event full bo‘lsa:

```python
JOIN -> waiting list
```

Kimdir leave qilsa:

```python
waitingdagi first user auto join bo‘ladi
```

Telegram bot orqali notification ketadi.

---

# RATING MODEL

```python
Rating
- id
- from_user
- to_user
- event_id
- stars
- created_at
```

---

# STARS

```python
1 -> 5
```

---

# NOTES

Event tugagandan keyin rating beriladi.

---

# REPORT MODEL

```python
Report
- id
- reporter_id
- target_user_id
- message
- created_at
```

---

# NOTES

Hozircha faqat oddiy shikoyat system.

Admin paneldan ko‘rinadi.

Message yoziladi xolos.

Moderation system hozircha yo‘q.

---

# ORGANIZER APPLICATION MODEL

```python
OrganizerApplication
- id
- user_id
- message
- status
- created_at
```

---

# STATUS

```python
choices = [
    "pending",
    "approved",
    "rejected"
]
```

---

# LOGIC

1. User organizer request yuboradi
2. Admin approve qiladi
3. is_organizer=True bo‘ladi

---

# USER ACHIEVEMENT MODEL

```python
Achievement
- id
- title
- icon
- description
```

---

# USER ACHIEVEMENT RELATION

```python
UserAchievement
- id
- user_id
- achievement_id
- created_at
```

---

# EXAMPLES

- 10 Events Joined
- Top Organizer
- 30 Games Played
- Chess Master

---

# AUTHENTICATION FLOW

---

# STEP 1
# TELEGRAM BOT AUTH

```http
POST /api/auth/telegram/
```

---

# REQUEST

```json
{
    "telegram_id": 123456789,
    "telegram_username": "dovudbek",
    "avatar": "image_url",
    "language": "uz_latn"
}
```

---

# RESPONSE

```json
{
    "access": "jwt_token",
    "refresh": "refresh_token"
}
```

---

# NOTES

Telegram start bosilganda:
- telegram_id auto olinadi
- fake login bo‘lmaydi

---

# STEP 2
# MINI APP ONBOARDING

```http
POST /api/auth/onboarding/
```

---

# REQUEST

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

# EVENT APIs

---

# GET ALL EVENTS

```http
GET /api/events/
```

---

# QUERY PARAMETERS

```http
?category=1
?today=true
?status=upcoming
?draft=false
```

---

# RESPONSE

```json
[
    {
        "id": 1,
        "title": "Chess Tournament",
        "category": {
            "id": 1,
            "title": "Chess",
            "icon": "icon"
        },
        "location": {
            "title": "Tashkent",
            "latitude": "41.31",
            "longitude": "69.24"
        },
        "event_date": "2026-05-20",
        "event_time": "18:00",
        "seats_left": 5,
        "participants": [
            {
                "avatar": "image"
            }
        ]
    }
]
```

---

# TODAY EVENTS

```http
GET /api/events/?today=true
```

---

# NOTES

Main page uchun.

Faqat bugungi eventlar.

---

# GET SINGLE EVENT

```http
GET /api/events/:id/
```

---

# CREATE EVENT

```http
POST /api/events/
```

---

# PERMISSION

```python
is_organizer=True
```

---

# REQUEST

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

# UPDATE EVENT

```http
PUT /api/events/:id/
```

---

# DELETE EVENT

Soft delete recommended.

```http
DELETE /api/events/:id/
```

---

# EVENT JOIN SYSTEM

---

# JOIN EVENT

```http
POST /api/events/:id/join/
```

---

# LOGIC

If:

```python
joined_users < total_seats
```

then:

```python
Attendance create
```

Else:

```python
WaitingList create
```

---

# LEAVE EVENT

```http
POST /api/events/:id/leave/
```

---

# LOGIC

1. Attendance cancelled bo‘ladi
2. WaitingList first user auto join bo‘ladi
3. Telegram notification ketadi

---

# ATTENDED CHECK SYSTEM

---

# MARK USER AS ATTENDED

```http
POST /api/events/:id/attendance/:user_id/
```

---

# PERMISSION

Faqat organizer.

---

# LOGIC

```python
joined -> attended
```

---

# PROFILE APIs

---

# MY PROFILE

```http
GET /api/profile/me/
```

---

# UPDATE PROFILE

```http
PUT /api/profile/me/
```

---

# USER PROFILE

```http
GET /api/profile/:id/
```

---

# RESPONSE

```json
{
    "full_name": "Dovudbek",
    "avatar": "image",
    "age": 21,
    "region": "Tashkent",
    "language": "uz_latn",
    "show_telegram": true,
    "telegram_username": "dovudbek",
    "total_attended": 15,
    "rating": 4.8,
    "interests": [],
    "achievements": [],
    "history": []
}
```

---

# HISTORY LOGIC

Attendance + Event orqali build qilinadi.

Separate history table yo‘q.

---

# LEADERBOARD APIs

---

# GET LEADERBOARD

```http
GET /api/leaderboard/
```

---

# RESPONSE

```json
[
    {
        "user": {
            "full_name": "Dovudbek",
            "avatar": "image"
        },
        "total_attended": 30,
        "rating": 4.9,
        "rates_count": 53
    }
]
```

---

# SEARCH APIs

---

# SEARCH EVENTS

```http
GET /api/events/search/?q=chess
```

---

# SEARCH BY

- title
- category
- organizer
- location

---

# ORGANIZER APIs

---

# SEND ORGANIZER REQUEST

```http
POST /api/organizer/request/
```

---

# REQUEST

```json
{
    "message": "I want to organize chess tournaments"
}
```

---

# ADMIN FLOW

1. Admin requestni ko‘radi
2. Approve qiladi
3. User organizer bo‘ladi

---

# REPORT APIs

---

# SEND REPORT

```http
POST /api/reports/
```

---

# REQUEST

```json
{
    "target_user_id": 5,
    "message": "Spam behavior"
}
```

---

# TELEGRAM NOTIFICATION SYSTEM

---

# ALL NOTIFICATIONS BOT ORQALI

UI notification system yo‘q.

---

# NOTIFICATIONS

- Event reminder
- Event cancelled
- Waiting list approved
- Organizer approved

---

# BUSINESS RULES

---

# EVENT CREATE RULES

- Faqat organizer create qila oladi
- Draft save mumkin
- Draft public ko‘rinmaydi

---

# EVENT JOIN RULES

- Bir user bir marta join qila oladi
- Event full bo‘lsa waiting listga tushadi

---

# RATING RULES

- Faqat event qatnashchilari rating bera oladi
- Event completed bo‘lishi kerak

---

# SECURITY RULES

---

# AUTH

Telegram verification required.

---

# PERMISSIONS

```python
Normal User:
- join event
- leave event
- rate users
- report users

Organizer:
- create event
- update event
- mark attendance

Admin:
- organizer approve
- reports view
```

---


Authentication:
- JWT

Task Queue:
- Celery

Cache:
- Redis

Deployment:
- Docker
- Nginx
- Gunicorn
```

---




---

# FINAL ARCHITECTURE NOTES

## IMPORTANT

### seats_left

❌ database field emas

✅ calculated field

---

### user_history

❌ alohida table emas

✅ Attendance orqali build qilinadi

---

### waiting list

Retention uchun juda muhim.

---

### organizer verification

Spam eventlarni kamaytiradi.

---

### telegram notifications

Primary notification system.

---

# FINAL STATUS

Architecture Level:
Production Ready MVP

Scalability:
High

Recommended Database:
PostgreSQL

Recommended API Style:
REST API (DRF)
