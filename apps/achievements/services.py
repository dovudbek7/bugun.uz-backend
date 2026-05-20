from .models import Achievement, UserAchievement


def award_joined_achievements(user):
    rules = [
        (10, "10 Events Joined", "Joined 10 events"),
        (30, "30 Games Played", "Attended 30 games"),
    ]
    for threshold, title, description in rules:
        if user.total_attended >= threshold:
            achievement, _ = Achievement.objects.get_or_create(
                title=title,
                defaults={"icon": "trophy", "description": description},
            )
            UserAchievement.objects.get_or_create(user=user, achievement=achievement)


def award_top_organizer(user):
    achievement, _ = Achievement.objects.get_or_create(
        title="Top Organizer",
        defaults={"icon": "star", "description": "Recognized as a top event organizer"},
    )
    UserAchievement.objects.get_or_create(user=user, achievement=achievement)
