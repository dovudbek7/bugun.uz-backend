from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.response import Response

from apps.common.permissions import IsAdminUser

from .models import Report
from .serializers import ReportCreateSerializer, ReportSerializer


@extend_schema(tags=["Reports"])
class ReportViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportCreateSerializer

    @extend_schema(
        summary="Submit a report against a user",
        responses={201: inline_serializer("ReportCreated", fields={"message": serializers.CharField()})},
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Report submitted"}, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Admin"])
class AdminReportViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Report.objects.select_related("reporter", "target_user")
    serializer_class = ReportSerializer
    permission_classes = [IsAdminUser]

    @extend_schema(summary="List all user reports")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
