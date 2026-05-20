# Community Event Platform — Backend

Production-ready Django REST API + Telegram Bot for offline community events (chess, mafia, board games, meetups).

## Stack

- **Django 4.x** + **DRF** — REST API
- **PostgreSQL** — Primary database
- **Redis** — Celery broker + result backend
- **Celery** — Async tasks & periodic tasks
- **aiogram 3.x** — Telegram Bot
- **SimpleJWT** — JWT authentication
- **drf-spectacular** — OpenAPI / Swagger docs
- **Docker Compose** — Full containerised setup

---

## Quick Start (Docker)

```bash
# 1. Clone and enter the project
git clone <repo> && cd bugun.uz-backend

# 2. Copy env file and set your values
cp .env.example .env

# 3. Start all services (API, bot, Celery, DB, Redis)
docker compose up --build

# 4. In another terminal — create superuser
docker compose exec web python manage.py createsuperuser

# 5. Seed demo data (10 users, 10 events, categories, etc.)
docker compose exec web python manage.py seed_data
```

Services after `docker compose up`:

| Service      | URL / Port                              |
|--------------|-----------------------------------------|
| REST API     | http://localhost:8000/api/              |
| Swagger Docs | http://localhost:8000/api/docs/         |
| Admin Panel  | http://localhost:8000/admin/            |
| Dashboard    | http://localhost:8000/dashboard/statistics/ |
| Reports Page | http://localhost:8000/dashboard/reports/ |
| Telegram Bot | Polling starts automatically            |

---

## Local Development (without Docker)

```bash
# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set env (PostgreSQL must be running locally)
export POSTGRES_HOST=localhost
export DJANGO_SETTINGS_MODULE=config.settings

# Migrations
python manage.py migrate

# Seed data
python manage.py seed_data

# Create superuser
python manage.py createsuperuser

# Run API
python manage.py runserver

# Run Celery worker (separate terminal)
celery -A config worker -l info

# Run Celery beat (separate terminal)
celery -A config beat -l info

# Run Telegram Bot (separate terminal)
python -m apps.telegram_bot.run
```

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

POSTGRES_DB=bugun
POSTGRES_USER=bugun
POSTGRES_PASSWORD=bugun
POSTGRES_HOST=db           # 'db' for Docker, 'localhost' for local dev
POSTGRES_PORT=5432

JWT_ACCESS_MINUTES=60
JWT_REFRESH_DAYS=14

BOT_TOKEN=8980123227:AAGkb2zjBGBiUCd9jzVQAKDVzVk9J8InGR8
MINI_APP_URL=https://t.me   # Replace with real Mini App URL

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
```

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/telegram/` | Login / register via Telegram |
| POST | `/api/auth/onboarding/` | Complete profile (mini app step 2) |
| POST | `/api/auth/refresh/` | Refresh JWT token |

### Events
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/events/` | List events (filter: `?category=1&today=true`) |
| POST | `/api/events/` | Create event (organizers only) |
| GET | `/api/events/:id/` | Event detail |
| PUT | `/api/events/:id/` | Update event |
| DELETE | `/api/events/:id/` | Cancel event |
| POST | `/api/events/:id/join/` | Join event (auto-waitlist if full) |
| POST | `/api/events/:id/leave/` | Leave event |
| GET | `/api/events/today/` | Today's upcoming events |
| GET | `/api/events/search/?q=chess` | Search events |
| GET | `/api/events/:id/participants/` | Participant list (organizer) |
| GET | `/api/events/:id/waiting-list/` | Waiting list (organizer) |
| POST | `/api/events/:id/attendance/:user_id/` | Mark user attended (organizer) |

### Maps
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/maps/` | Upcoming events with coordinates |

### Leaderboard & Profile
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/leaderboard/` | Top players by attendance + rating |
| GET | `/api/profile/me/` | My profile |
| PUT | `/api/profile/me/` | Update my profile |
| GET | `/api/profile/:id/` | Other user's profile |
| GET | `/api/history/me/` | My event history |
| GET | `/api/achievements/me/` | My achievements |

### Categories, Interests, Locations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/categories/` | All categories |
| GET | `/api/interests/` | All interests |
| GET | `/api/locations/` | All locations |
| POST | `/api/locations/` | Create location (organizers) |

### Organizer, Ratings, Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/organizer/request/` | Apply for organizer / check status |
| POST | `/api/ratings/` | Rate a user (post-event) |
| POST | `/api/reports/` | Report a user |
| GET | `/api/admin/reports/` | All reports (admin only) |
| GET | `/api/admin/organizer-requests/` | Organizer applications (admin) |
| POST | `/api/admin/organizer-requests/:id/approve/` | Approve organizer |
| POST | `/api/admin/organizer-requests/:id/reject/` | Reject organizer |

---

## Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Register account, request phone number |
| `/profile` | View name, rating, total games, organizer status |
| `/games` | View joined / upcoming / completed events |
| `/location` | Share current location |
| `/help` | Show all available commands |

The bot sends automatic Telegram notifications for:
- Organizer request approved
- Moved from waiting list to joined
- Event reminder (24h before)
- Event cancelled

---

## Admin Dashboard

Custom statistics dashboard at `/dashboard/statistics/` (staff only):
- User stats: total, today's registrations, organizer count
- Event stats: total, today, upcoming, completed, cancelled, drafts
- Attendance stats: total joined, most popular event
- Category stats: most used category
- Reports summary with link to reports page

Reports page at `/dashboard/reports/` — all user reports in card layout.

---

## Django Admin

At `/admin/` — manage:
- Users (with all Telegram fields)
- Events (with status, draft, organizer filters)
- Attendance & Waiting List
- Organizer Applications (bulk approve/reject actions)
- Categories, Interests, Locations
- Ratings, Reports, Achievements

---

## Celery Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| `complete_past_events` | Every 10 min | Auto-complete past events |
| `send_event_reminders` | Every 15 min | Send 24h reminders via bot |
| `send_event_notification` | On-demand | Push Telegram notifications |

---

## Business Rules

- Users cannot join the same event twice
- Cannot join cancelled or completed events
- Cannot join draft events
- `seats_left` calculated dynamically: `total_seats - joined_count`
- When leaving → first waiting-list user auto-joins with Telegram notification
- Users can only rate each other if both attended the same completed event
- Cannot create events without organizer status
- Organizer status requires admin approval via application flow
- User history is built from Attendance + Event relations (no separate table)

---

## Testing

```bash
# After seed_data — get a JWT token:
curl -X POST http://localhost:8000/api/auth/telegram/ \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": 900001, "telegram_username": "user1"}'

# Use the token:
curl http://localhost:8000/api/events/ \
  -H "Authorization: Bearer <access_token>"

# Full API docs:
open http://localhost:8000/api/docs/
```
