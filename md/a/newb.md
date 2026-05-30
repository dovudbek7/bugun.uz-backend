# EVENT COMMUNITY PLATFORM
# FULL BACKEND + TELEGRAM BOT ARCHITECTURE DOCUMENTATION
## Django REST Framework + Telegram Bot + Mini App

---

# PROJECT OVERVIEW

Bu platforma offline community event platformasi hisoblanadi.

Asosiy maqsad:
- chess
- mafia
- board games
- meetup
- offline games

uchun userlarni yig‘ish va event management qilish.

Platformada:
- Telegram Bot
- Telegram Mini App
- Django REST API

birgalikda ishlaydi.

---

# MAIN SYSTEM PARTS

```text
1. Telegram Bot
2. Telegram Mini App
3. Django REST Backend
4. PostgreSQL Database
5. Redis + Celery
```

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
├── organizer/
├── ratings/
├── reports/
├── interests/
├── categories/
├── locations/
├── achievements/
├── telegram_bot/
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

# USER FIELD LOGIC

---

## telegram_id

Telegram orqali auto olinadi.

Unique bo‘lishi kerak.

---

## telegram_username

Optional.

Agar mavjud bo‘lsa profileda ko‘rinadi.

---

## avatar

Telegram profile image.

Agar image bo‘lmasa:
frontend first letter chiqaradi.

---

## show_telegram

```python
True
```

bo‘lsa:
- telegram username
- telegram profile

boshqa userlarga ko‘rinadi.

---

## total_attended

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

# USER INTEREST MODEL

```python
UserInterest
- id
- user_id
- interest_id
```

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
- is_draft
- status
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

# IMPORTANT

## seats_left

Databasega saqlanmaydi.

Runtime calculate qilinadi.

```python
seats_left = total_seats - joined_users
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

# WAITING LIST MODEL

```python
WaitingList
- id
- user_id
- event_id
- created_at
```

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

# ORGANIZER STATUS

```python
choices = [
    "pending",
    "approved",
    "rejected"
]
```

---

# ACHIEVEMENT MODEL

```python
Achievement
- id
- title
- icon
- description
```

---

# USER ACHIEVEMENT MODEL

```python
UserAchievement
- id
- user_id
- achievement_id
```

---

# TELEGRAM BOT SYSTEM

---

# BOT RESPONSIBILITIES

Telegram bot:
- authentication
- notifications
- commands
- location sharing
- event info
- mini app open button

uchun ishlatiladi.

---

# BOT TOKEN

```env
BOT_TOKEN=8980123227:AAGkb2zjBGBiUCd9jzVQAKDVzVk9J8InGR8
```

---

# REQUIRED BOT LIBRARY

Recommended:

```python
aiogram
```

---

# BOT COMMANDS

---

# /start

## Logic

1. User databasega yoziladi
2. telegram_id olinadi
3. avatar olinadi
4. telegram_username olinadi
5. language select qilinadi
6. phone number request qilinadi
7. mini app button chiqariladi

---

# /profile

## Logic

User profile ma’lumotlarini chiqaradi.

---

## Example Response

```text
Name: Dovudbek
Rating: 4.8
Total Games: 15
Organizer: Yes
```

---

# /games

## Logic

User joined bo‘lgan game/eventlarni chiqaradi.

---

## Example

```text
1. Chess Tournament
2. Mafia Night
3. Board Games Meetup
```

---

# /help

## Logic

Barcha commandlarni chiqaradi.

---

# /location

## Logic

Telegram location button chiqaradi.

User location yuboradi.

---

# BOT BUTTONS

---

# SHARE PHONE BUTTON

Telegram keyboard orqali:
phone number request qiladi.

---

# SHARE LOCATION BUTTON

Telegram keyboard orqali:
location request qiladi.

---

# MINI APP BUTTON

Telegram mini appni ochadi.

---

# TELEGRAM BOT NOTIFICATIONS

---

# EVENT REMINDER

```text
Your event starts in 1 hour
```

---

# WAITING LIST APPROVED

```text
You joined the event from waiting list
```

---

# ORGANIZER APPROVED

```text
Your organizer request approved
```

---

# EVENT CANCELLED

```text
Event cancelled by organizer
```

---

# AUTHENTICATION FLOW

---

# STEP 1
# TELEGRAM BOT

```http
POST /api/auth/telegram/
```

---

# TELEGRAM DATA

```json
{
    "telegram_id": 123456789,
    "telegram_username": "dovudbek",
    "avatar": "image_url",
    "language": "uz_latn",
    "phone_number": "+998901234567"
}
```

---

# RESPONSE

```json
{
    "access": "jwt_access",
    "refresh": "jwt_refresh"
}
```

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
    "show_telegram": true,
    "interests": [1, 2, 3]
}
```

---

# GET APIs

---

# MAPS API

## Endpoint

```http
GET /api/maps/
```

---

## RESPONSE

```json
[
    {
        "name": "Chess Tournament",
        "location": {
            "title": "Magic City",
            "longitude": "69.24",
            "latitude": "41.31"
        },
        "icon": "icon",
        "time": "18:00",
        "seats_left": 5
    }
]
```

---

# EVENTS API

## Endpoint

```http
GET /api/events/
```

---

## QUERY PARAMETERS

```http
?category=1
?today=true
?page=1
```

---

## RESPONSE

```json
[
    {
        "title": "Chess Tournament",
        "location": {
            "title": "Magic City"
        },
        "time": "18:00",
        "seats_left": 5,
        "participants": [
            {
                "avatar": "image"
            }
        ],
        "tag": {
            "quick": true
        }
    }
]
```

---

# TODAY EVENTS API

## Endpoint

```http
GET /api/events/today/
```

---

## LOGIC

Faqat bugungi eventlar.

Main page uchun.

---

# SINGLE EVENT API

## Endpoint

```http
GET /api/events/:id/
```

---

# LEADERBOARD API

## Endpoint

```http
GET /api/leaderboard/
```

---

## RESPONSE

```json
[
    {
        "icon": "image",
        "name": "Dovudbek",
        "total_attended": 25,
        "rating": 4.9,
        "rates_count": 50
    }
]
```

---

# PROFILE API

## Endpoint

```http
GET /api/profile/me/
```

---

## RESPONSE

```json
{
    "name": "Dovudbek",
    "image": "image",
    "age": 21,
    "region": "Tashkent",
    "telegram_username": "dovudbek",
    "language": "uz_latn",
    "phone_number": "+998901234567",
    "show_telegram": true,
    "total_attended": 15,
    "rating": 4.8,
    "interests": [],
    "is_organizer": true,
    "user_history": []
}
```

---

# CATEGORY API

## Endpoint

```http
GET /api/categories/
```

---

# SEARCH EVENTS API

## Endpoint

```http
GET /api/events/search/?q=chess
```

---

# SEARCH FIELDS

- title
- category
- organizer
- location

---

# POST APIs

---

# CREATE EVENT

## Endpoint

```http
POST /api/events/
```

---

# PERMISSION

Only organizers.

---

# REQUEST

```json
{
    "type": 1,
    "date": "2026-05-20",
    "time": "18:00",
    "location": 1,
    "attendance_count": 20,
    "description": "Weekend chess games",
    "is_draft": false
}
```

---

# JOIN EVENT

## Endpoint

```http
POST /api/events/:id/join/
```

---

# LOGIC

If seats available:

```python
Attendance create
```

Else:

```python
WaitingList create
```

---

# LEAVE EVENT

## Endpoint

```http
POST /api/events/:id/leave/
```

---

# ORGANIZER REQUEST

## Endpoint

```http
POST /api/organizer/request/
```

---

# REQUEST

```json
{
    "message": "I want organize chess events"
}
```

---

# SEND REPORT

## Endpoint

```http
POST /api/reports/
```

---

## REQUEST

```json
{
    "target_user_id": 5,
    "message": "Spam behavior"
}
```

---

# RATE USER

## Endpoint

```http
POST /api/ratings/
```

---

## REQUEST

```json
{
    "to_user": 5,
    "event_id": 1,
    "stars": 5
}
```

---

# ATTENDANCE MANAGEMENT

---

# MARK USER AS ATTENDED

## Endpoint

```http
POST /api/events/:id/attendance/:user_id/
```

---

# PERMISSION

Only organizer.

---

# USER HISTORY STRUCTURE

```json
[
    {
        "icon": "icon",
        "title": "Chess Tournament",
        "date": "2026-05-20",
        "total_attended_people": 20,
        "is_organized": false,
        "total_attends": 0,
        "is_draft": false
    }
]
```

---

# BUSINESS RULES

---

# EVENT RULES

- only organizers can create event
- drafts publicda ko‘rinmaydi
- cancelled eventsga join qilib bo‘lmaydi
- completed eventsga join qilib bo‘lmaydi

---

# ATTENDANCE RULES

- one user -> one attendance
- organizer attended status qo‘yadi

---

# WAITING LIST RULES

- event full bo‘lsa waiting list ishlaydi
- first waiting user auto join bo‘ladi

---

# RATING RULES

- faqat event participantlari rating bera oladi

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
- attendance manage

Admin:
- organizer approve
- reports view
```

---

# REQUIRED PACKAGES

```python
Django
djangorestframework
psycopg2
simplejwt
drf-spectacular
django-filter
redis
celery
aiogram
python-dotenv
Pillow
```

---

# REQUIRED FILES

```bash
Dockerfile
docker-compose.yml
requirements.txt
.env.example
README.md
```

---

# REQUIRED README CONTENT

- setup
- docker
- migrations
- create superuser
- run bot
- run celery
- swagger url
- testing

---

# MOCK DATA

Create:

```bash
python manage.py seed_data
```

---

# MOCK DATA MUST GENERATE

- 10 users
- 10 events
- attendance
- organizer requests
- ratings
- categories
- interests

---

# PERFORMANCE

Use:
- select_related
- prefetch_related
- pagination
- indexes

---

# IMPORTANT NOTES

## seats_left

NOT database field.

---

## user_history

NOT separate table.

---

## telegram notifications

All notifications bot orqali yuboriladi.

---

# FINAL MVP STATUS

Architecture:
Production-ready scalable MVP.

Backend:
DRF

Bot:
Aiogram

Database:
PostgreSQL

Authentication:
Telegram + JWT
