from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.achievements.models import Achievement, UserAchievement
from apps.attendance.models import Attendance, WaitingList
from apps.categories.models import Category
from apps.events.models import Event
from apps.interests.models import Interest, UserInterest
from apps.locations.models import Location
from apps.organizer.models import OrganizerApplication
from apps.ratings.models import Rating


User = get_user_model()


class Command(BaseCommand):
    help = "Seed development data for immediate API testing."

    @transaction.atomic
    def handle(self, *args, **options):
        categories = [
            Category.objects.get_or_create(title=title, defaults={"icon": icon, "color": color})[0]
            for title, icon, color in [
                ("Chess", "chess", "#111827"),
                ("Mafia", "mask", "#B91C1C"),
                ("Board Games", "dice", "#047857"),
                ("Meetup", "users", "#2563EB"),
            ]
        ]
        interests = [
            Interest.objects.get_or_create(title=title, defaults={"icon": icon})[0]
            for title, icon in [
                ("Chess", "chess"),
                ("Mafia", "mask"),
                ("Board Games", "dice"),
                ("Football", "ball"),
                ("Networking", "users"),
            ]
        ]
        locations = [
            Location.objects.get_or_create(
                title=f"Venue {idx}",
                defaults={
                    "latitude": 41.30 + idx / 100,
                    "longitude": 69.20 + idx / 100,
                    "address": f"Tashkent, street {idx}",
                },
            )[0]
            for idx in range(1, 6)
        ]

        users = []
        for idx in range(1, 11):
            user, _ = User.objects.get_or_create(
                telegram_id=900000 + idx,
                defaults={
                    "username": f"tg_{900000 + idx}",
                    "telegram_username": f"user{idx}",
                    "full_name": f"Demo User {idx}",
                    "age": 18 + idx,
                    "region": "Tashkent",
                    "phone_number": f"+9989000000{idx:02d}",
                    "is_organizer": idx <= 3,
                },
            )
            users.append(user)
            for interest in interests[: (idx % len(interests)) + 1]:
                UserInterest.objects.get_or_create(user=user, interest=interest)

        now = timezone.localdate()
        events = []
        for idx in range(1, 11):
            event, _ = Event.objects.get_or_create(
                title=f"Demo Event {idx}",
                defaults={
                    "organizer": users[idx % 3],
                    "category": categories[idx % len(categories)],
                    "location": locations[idx % len(locations)],
                    "description": f"Community activity #{idx}",
                    "event_date": now + timedelta(days=idx - 5),
                    "event_time": timezone.datetime.strptime("18:00", "%H:%M").time(),
                    "total_seats": 5 + idx,
                    "status": Event.STATUS_COMPLETED if idx < 5 else Event.STATUS_UPCOMING,
                    "is_draft": False,
                },
            )
            events.append(event)

        for idx, event in enumerate(events):
            for user in users[: min(5, len(users))]:
                status = Attendance.STATUS_ATTENDED if event.status == Event.STATUS_COMPLETED else Attendance.STATUS_JOINED
                Attendance.objects.get_or_create(user=user, event=event, defaults={"status": status})
            if idx % 3 == 0:
                WaitingList.objects.get_or_create(user=users[-1], event=event)

        for user in users:
            user.total_attended = Attendance.objects.filter(user=user, status=Attendance.STATUS_ATTENDED).count()
            user.save(update_fields=["total_attended"])

        completed = [event for event in events if event.status == Event.STATUS_COMPLETED]
        for event in completed:
            Rating.objects.get_or_create(from_user=users[0], to_user=users[1], event=event, defaults={"stars": 5})
            Rating.objects.get_or_create(from_user=users[1], to_user=users[0], event=event, defaults={"stars": 4})
        for user in users[:2]:
            received = Rating.objects.filter(to_user=user)
            if received.exists():
                user.rating = sum(item.stars for item in received) / received.count()
                user.save(update_fields=["rating"])

        for user in users[3:6]:
            OrganizerApplication.objects.get_or_create(
                user=user,
                defaults={"message": "I want to organize community events.", "status": OrganizerApplication.STATUS_PENDING},
            )

        achievement, _ = Achievement.objects.get_or_create(
            title="10 Events Joined",
            defaults={"icon": "trophy", "description": "Joined 10 events"},
        )
        UserAchievement.objects.get_or_create(user=users[0], achievement=achievement)

        self.stdout.write(self.style.SUCCESS("Seed data created: 10 users, 10 events, categories, interests, attendance, leaderboard, organizer requests."))
