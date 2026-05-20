"""
python manage.py generate_mock

Generates ~100+ realistic mock records for development/testing:
  - 20 users (8 organizers)
  - 6 categories with translations
  - 12 interests with translations
  - 15 locations across Tashkent
  - 30 events (mix of statuses)
  - ~150 attendance records
  - 20 ratings
  - 10 reports
  - 8 organizer applications
  - 5 achievements
"""
import random
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
from apps.reports.models import Report

User = get_user_model()

CATEGORIES = [
    ("Chess", "Шахматы", "Chess", "♟️", "#1e293b"),
    ("Mafia", "Мафия", "Mafia", "🎭", "#7f1d1d"),
    ("Board Games", "Настольные игры", "Board Games", "🎲", "#14532d"),
    ("Meetup", "Встреча", "Meetup", "🤝", "#1e3a5f"),
    ("Football", "Футбол", "Football", "⚽", "#065f46"),
    ("Poker", "Покер", "Poker", "🃏", "#4c1d95"),
]

INTERESTS = [
    ("Chess", "Шахматы", "Chess", "♟️"),
    ("Mafia", "Мафия", "Mafia", "🎭"),
    ("Board Games", "Настольные игры", "Board Games", "🎲"),
    ("Football", "Футбол", "Football", "⚽"),
    ("Poker", "Покер", "Poker", "🃏"),
    ("Networking", "Нетворкинг", "Networking", "🤝"),
    ("Gaming", "Игры", "Gaming", "🎮"),
    ("Reading", "Чтение", "Reading", "📚"),
    ("Music", "Музыка", "Music", "🎵"),
    ("Photography", "Фотография", "Photography", "📸"),
    ("Travel", "Путешествия", "Travel", "✈️"),
    ("Cooking", "Кулинария", "Cooking", "🍳"),
]

LOCATIONS = [
    ("Magic City Mall", 41.2995, 69.2401, "Yunusobod, Tashkent"),
    ("Tashkent City", 41.2856, 69.2088, "Mirzo Ulugbek, Tashkent"),
    ("Hamid Olimjon Metro", 41.3003, 69.2752, "Shayxontohur, Tashkent"),
    ("Central Park", 41.3169, 69.2401, "Chilonzor, Tashkent"),
    ("Amir Timur Square", 41.2994, 69.2408, "Mirzo Ulugbek, Tashkent"),
    ("Chorsu Bazaar", 41.3267, 69.2346, "Shayxontohur, Tashkent"),
    ("Minor Mosque", 41.2852, 69.2176, "Yunusobod, Tashkent"),
    ("National Library", 41.2991, 69.2751, "Mirzo Ulugbek, Tashkent"),
    ("Grand Mir Hotel", 41.2953, 69.2742, "Mirzo Ulugbek, Tashkent"),
    ("Navoi Opera House", 41.2989, 69.2706, "Mirzo Ulugbek, Tashkent"),
    ("Alisher Navoi Park", 41.3103, 69.2594, "Yunusobod, Tashkent"),
    ("IT Park Tashkent", 41.2840, 69.1997, "Kibray, Tashkent"),
    ("The Tashkent", 41.2999, 69.2400, "Mirzo Ulugbek, Tashkent"),
    ("TSUE Campus", 41.3236, 69.2706, "Shayxontohur, Tashkent"),
    ("Zamin Hub", 41.2910, 69.2068, "Yunusobod, Tashkent"),
]

USERS = [
    ("Dovudbek Xabibullayev", "dovudbek_x", "Tashkent"),
    ("Jasur Toshmatov", "jasur_t", "Samarkand"),
    ("Nilufar Karimova", "nilufar_k", "Tashkent"),
    ("Bobur Yusupov", "bobur_y", "Namangan"),
    ("Zulfiya Abdullayeva", "zulfiya_a", "Tashkent"),
    ("Sarvarbek Rахimov", "sarvar_r", "Fergana"),
    ("Madina Hasanova", "madina_h", "Tashkent"),
    ("Ulugbek Normatov", "ulugbek_n", "Bukhara"),
    ("Shahlo Mirzayeva", "shahlo_m", "Tashkent"),
    ("Firdavs Qodirov", "firdavs_q", "Andijan"),
    ("Aziz Tursunov", "aziz_t", "Tashkent"),
    ("Oydin Xolmatova", "oydin_x", "Namangan"),
    ("Murod Begmatov", "murod_b", "Tashkent"),
    ("Sarvinoz Usmonova", "sarvinoz_u", "Samarkand"),
    ("Bahrom Nazarov", "bahrom_n", "Tashkent"),
    ("Dildora Yusupova", "dildora_y", "Fergana"),
    ("Sanjar Islomov", "sanjar_i", "Tashkent"),
    ("Kamola Rашidova", "kamola_r", "Bukhara"),
    ("Otabek Mamatov", "otabek_m", "Tashkent"),
    ("Hulkar Sodiqova", "hulkar_s", "Namangan"),
]

EVENT_TEMPLATES = [
    ("Chess Championship #{n}", 0),
    ("Mafia Night #{n}", 1),
    ("Board Games Friday #{n}", 2),
    ("Tech Meetup #{n}", 3),
    ("Football Match #{n}", 4),
    ("Poker Evening #{n}", 5),
    ("Blitz Chess #{n}", 0),
    ("Mafia Tournament #{n}", 1),
    ("Strategy Games #{n}", 2),
    ("Startup Meetup #{n}", 3),
]

DESCRIPTIONS = [
    "Join us for an exciting community event. All skill levels welcome!",
    "Weekly community gathering. Come meet new people and have fun.",
    "Competitive tournament with prizes for top players.",
    "Casual friendly game for all levels. Beginners welcome.",
    "Professional level event. Experience required.",
    "Special themed event. Don't miss it!",
    "Monthly championship. Register early, limited seats!",
    "Community favorites event. Always fun, always memorable.",
]


class Command(BaseCommand):
    help = "Generate 100+ realistic mock records for development testing."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("🚀 Generating mock data...")

        # ── Categories ──────────────────────────────────────────────────────────
        categories = []
        for title, title_ru, title_en, icon, color in CATEGORIES:
            cat, _ = Category.objects.get_or_create(
                title=title,
                defaults={"title_ru": title_ru, "title_en": title_en, "icon": icon, "color": color},
            )
            categories.append(cat)
        self.stdout.write(f"  ✅ {len(categories)} categories")

        # ── Interests ───────────────────────────────────────────────────────────
        interests = []
        for title, title_ru, title_en, icon in INTERESTS:
            interest, _ = Interest.objects.get_or_create(
                title=title,
                defaults={"title_ru": title_ru, "title_en": title_en, "icon": icon},
            )
            interests.append(interest)
        self.stdout.write(f"  ✅ {len(interests)} interests")

        # ── Locations ───────────────────────────────────────────────────────────
        locations = []
        for title, lat, lon, address in LOCATIONS:
            loc, _ = Location.objects.get_or_create(
                title=title,
                defaults={"latitude": lat, "longitude": lon, "address": address},
            )
            locations.append(loc)
        self.stdout.write(f"  ✅ {len(locations)} locations")

        # ── Users ───────────────────────────────────────────────────────────────
        users = []
        for idx, (full_name, username, region) in enumerate(USERS, start=1):
            tg_id = 800000 + idx
            is_org = idx <= 8
            lang = ["uz_latn", "uz_cyrl", "ru", "en"][idx % 4]
            user, _ = User.objects.get_or_create(
                telegram_id=tg_id,
                defaults={
                    "username": f"mock_{username}",
                    "telegram_username": username,
                    "full_name": full_name,
                    "age": 18 + (idx % 15),
                    "region": region,
                    "phone_number": f"+9989{tg_id}",
                    "is_organizer": is_org,
                    "language": lang,
                    "show_telegram": idx % 3 != 0,
                },
            )
            # Assign interests (2-5 random)
            for interest in random.sample(interests, k=min(random.randint(2, 5), len(interests))):
                UserInterest.objects.get_or_create(user=user, interest=interest)
            users.append(user)
        self.stdout.write(f"  ✅ {len(users)} users")

        organizers = [u for u in users if u.is_organizer]
        today = timezone.localdate()

        # ── Events (30 total) ───────────────────────────────────────────────────
        events = []
        for n in range(1, 31):
            template, cat_idx = EVENT_TEMPLATES[(n - 1) % len(EVENT_TEMPLATES)]
            title = template.format(n=n)
            days_offset = (n * 3) - 45   # spread across past + future
            event_date = today + timedelta(days=days_offset)

            if days_offset < -3:
                status = Event.STATUS_COMPLETED
            elif days_offset < 0 and n % 7 == 0:
                status = Event.STATUS_CANCELLED
            else:
                status = Event.STATUS_UPCOMING

            is_draft = (n % 10 == 0) and status == Event.STATUS_UPCOMING
            hour = 16 + (n % 5)

            event, _ = Event.objects.get_or_create(
                title=title,
                defaults={
                    "organizer": organizers[n % len(organizers)],
                    "category": categories[cat_idx],
                    "location": locations[n % len(locations)],
                    "description": DESCRIPTIONS[n % len(DESCRIPTIONS)],
                    "event_date": event_date,
                    "event_time": f"{hour:02d}:00",
                    "total_seats": random.choice([8, 10, 12, 15, 20]),
                    "status": status,
                    "is_draft": is_draft,
                },
            )
            events.append(event)
        self.stdout.write(f"  ✅ {len(events)} events")

        # ── Attendance ──────────────────────────────────────────────────────────
        att_created = 0
        waiting_created = 0
        for event in events:
            if event.is_draft:
                continue
            # Each event gets 4-12 attendees
            attendees = random.sample(users, k=min(random.randint(4, 12), len(users)))
            for i, user in enumerate(attendees):
                if user == event.organizer:
                    continue
                att_status = (
                    Attendance.STATUS_ATTENDED
                    if event.status == Event.STATUS_COMPLETED
                    else Attendance.STATUS_JOINED
                )
                att, created = Attendance.objects.get_or_create(
                    user=user, event=event, defaults={"status": att_status}
                )
                if created:
                    att_created += 1
                # Add some to waiting list
                if i >= event.total_seats and event.status == Event.STATUS_UPCOMING:
                    WaitingList.objects.get_or_create(user=user, event=event)
                    waiting_created += 1
        self.stdout.write(f"  ✅ {att_created} attendance records, {waiting_created} waiting list entries")

        # Update total_attended for each user
        for user in users:
            user.total_attended = Attendance.objects.filter(user=user, status=Attendance.STATUS_ATTENDED).count()
            user.save(update_fields=["total_attended"])

        # ── Ratings ─────────────────────────────────────────────────────────────
        from django.db.models import Avg
        completed_events = [e for e in events if e.status == Event.STATUS_COMPLETED]
        rating_count = 0
        for event in completed_events[:10]:
            attendances = list(
                Attendance.objects.filter(event=event, status=Attendance.STATUS_ATTENDED).select_related("user")
            )
            for i, att_a in enumerate(attendances[:4]):
                for att_b in attendances[i + 1: i + 3]:
                    if att_a.user == att_b.user:
                        continue
                    stars = random.randint(3, 5)
                    _, created = Rating.objects.get_or_create(
                        from_user=att_a.user,
                        to_user=att_b.user,
                        event=event,
                        defaults={"stars": stars},
                    )
                    if created:
                        rating_count += 1

        # Recalculate ratings
        for user in users:
            agg = Rating.objects.filter(to_user=user).aggregate(avg=Avg("stars"))
            if agg["avg"]:
                user.rating = round(agg["avg"], 2)
                user.save(update_fields=["rating"])
        self.stdout.write(f"  ✅ {rating_count} ratings")

        # ── Reports ─────────────────────────────────────────────────────────────
        messages = [
            "Spam messages in chat",
            "Rude behavior at event",
            "No-show without cancellation",
            "Inappropriate language",
            "Suspicious activity",
        ]
        report_count = 0
        for i in range(10):
            reporter = users[i % len(users)]
            target = users[(i + 3) % len(users)]
            if reporter == target:
                continue
            _, created = Report.objects.get_or_create(
                reporter=reporter,
                target_user=target,
                defaults={"message": messages[i % len(messages)]},
            )
            if created:
                report_count += 1
        self.stdout.write(f"  ✅ {report_count} reports")

        # ── Organizer Applications ───────────────────────────────────────────────
        non_organizers = [u for u in users if not u.is_organizer]
        app_count = 0
        statuses = [OrganizerApplication.STATUS_PENDING, OrganizerApplication.STATUS_APPROVED,
                    OrganizerApplication.STATUS_REJECTED]
        for i, user in enumerate(non_organizers[:8]):
            _, created = OrganizerApplication.objects.get_or_create(
                user=user,
                defaults={
                    "message": f"I want to organize community events in {user.region}.",
                    "status": statuses[i % len(statuses)],
                },
            )
            if created:
                app_count += 1
        self.stdout.write(f"  ✅ {app_count} organizer applications")

        # ── Achievements ────────────────────────────────────────────────────────
        achievement_defs = [
            ("First Game", "🎮", "Attended first event"),
            ("10 Events Joined", "🏆", "Joined 10 events"),
            ("30 Games Played", "⭐", "Attended 30 games"),
            ("Top Organizer", "👑", "Recognized as a top event organizer"),
            ("Chess Master", "♟️", "Won 5 chess events"),
        ]
        ach_count = 0
        for title, icon, description in achievement_defs:
            ach, _ = Achievement.objects.get_or_create(
                title=title, defaults={"icon": icon, "description": description}
            )
            for user in random.sample(users, k=min(3, len(users))):
                _, created = UserAchievement.objects.get_or_create(user=user, achievement=ach)
                if created:
                    ach_count += 1
        self.stdout.write(f"  ✅ {ach_count} achievement records")

        total = (
            len(categories) + len(interests) + len(locations) +
            len(users) + len(events) + att_created +
            rating_count + report_count + app_count + ach_count
        )
        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 Done! Total records created: {total}\n"
            f"   Users: {len(users)} | Events: {len(events)} | "
            f"Attendance: {att_created} | Ratings: {rating_count}"
        ))
