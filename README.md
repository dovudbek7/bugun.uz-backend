# Community Event Platform Backend

Django REST Framework backend for Telegram-authenticated community events: chess, mafia, board games, meetups, attendance, waiting lists, organizer approvals, ratings, reports, achievements, and leaderboard.

## Stack

- Django + Django REST Framework
- PostgreSQL only
- JWT via `djangorestframework-simplejwt`
- Redis + Celery + Celery Beat
- Telegram Bot API notifications
- Swagger/OpenAPI via `drf-spectacular`

## Docker Setup

```bash
cp .env.example .env
docker compose up --build
```

Run migrations and create an admin user:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py seed_data
```

API docs:

- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI schema: `http://localhost:8000/api/schema/`
- Django admin: `http://localhost:8000/admin/`

## Local Setup

PostgreSQL and Redis must be running. This project does not use SQLite.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data
python manage.py runserver
```

Run workers:

```bash
celery -A config worker -l info
celery -A config beat -l info
```

## Main API Paths

- `POST /api/auth/telegram/`
- `POST /api/auth/onboarding/`
- `POST /api/auth/refresh/`
- `GET|PUT /api/profile/me/`
- `GET /api/profile/<id>/`
- `GET /api/categories/`
- `GET /api/interests/`
- `GET|POST /api/locations/`
- `GET|POST /api/events/`
- `GET|PUT|DELETE /api/events/<id>/`
- `GET /api/events/search/?q=chess`
- `POST /api/events/<id>/join/`
- `POST /api/events/<id>/leave/`
- `GET /api/events/<id>/participants/`
- `POST /api/events/<id>/attendance/<user_id>/`
- `GET /api/events/<id>/waiting-list/`
- `POST /api/ratings/`
- `GET /api/leaderboard/`
- `GET|POST /api/organizer/request/`
- `POST /api/reports/`
- `GET /api/achievements/me/`
- `GET /api/history/me/`
- `GET /api/admin/organizer-requests/`
- `POST /api/admin/organizer-requests/<id>/approve/`
- `POST /api/admin/organizer-requests/<id>/reject/`
- `GET /api/admin/reports/`

## Testing

After seeding, log in with one of the generated Telegram IDs:

```bash
curl -X POST http://localhost:8000/api/auth/telegram/ \
  -H "Content-Type: application/json" \
  -d '{"telegram_id":900001,"telegram_username":"user1","avatar":"","language":"uz_latn"}'
```

Use the returned access token:

```bash
curl http://localhost:8000/api/events/ \
  -H "Authorization: Bearer <access>"
```

## Business Rules Implemented

- `seats_left` is calculated dynamically from attendance and is not stored.
- User history is built from `Attendance` + `Event`.
- `(user, event)` attendance uniqueness prevents duplicate joins.
- Full events place users into a waiting list.
- Leaving an event promotes the first waiting user and sends a Telegram notification asynchronously.
- Only approved organizers can create events and manage attendance.
- Ratings require both users to have attended a completed event.
- Draft events are hidden from public listing and search.
