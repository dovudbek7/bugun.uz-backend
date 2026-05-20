from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from apps.common.permissions import IsAdminUser

from .models import Report
from .serializers import ReportCreateSerializer, ReportSerializer


class ReportViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Report submitted"}, status=status.HTTP_201_CREATED)


class AdminReportViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Report.objects.select_related("reporter", "target_user")
    serializer_class = ReportSerializer
    permission_classes = [IsAdminUser]
