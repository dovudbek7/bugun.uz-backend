from rest_framework.generics import ListAPIView

from .models import Achievement
from .serializers import AchievementSerializer


class MyAchievementsView(ListAPIView):
    serializer_class = AchievementSerializer
    pagination_class = None

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Achievement.objects.none()
        return Achievement.objects.filter(user_achievements__user=self.request.user)
