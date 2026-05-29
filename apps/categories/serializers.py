from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "name", "title_ru", "title_en", "icon", "color")

    def get_name(self, obj):
        request = self.context.get("request")
        lang = "uz_latn"
        if request:
            lang = (
                request.query_params.get("lang")
                or (request.user.language if request.user.is_authenticated and hasattr(request.user, "language") else "uz_latn")
            )
        return obj.get_title(lang)


class CategoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "title", "title_ru", "title_en", "icon", "color")
