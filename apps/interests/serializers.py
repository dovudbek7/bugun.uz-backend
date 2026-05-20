from rest_framework import serializers

from .models import Interest


class InterestSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = Interest
        fields = ("id", "title", "title_ru", "title_en", "icon")

    def get_title(self, obj):
        request = self.context.get("request")
        lang = "uz_latn"
        if request:
            lang = (
                request.query_params.get("lang")
                or (request.user.language if request.user.is_authenticated and hasattr(request.user, "language") else "uz_latn")
            )
        return obj.get_title(lang)
