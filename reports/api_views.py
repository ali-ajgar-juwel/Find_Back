from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from .models import Category, ItemReport, ClaimRequest
from .serializers import CategorySerializer, ItemReportSerializer, ClaimRequestSerializer

# Cache public GET responses for 60 seconds. Cookie variation avoids mixing
# browsable-API/session states between logged-in and anonymous users.
@method_decorator(cache_page(60), name="dispatch")
@method_decorator(vary_on_cookie, name="dispatch")
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

@method_decorator(cache_page(60), name="dispatch")
@method_decorator(vary_on_cookie, name="dispatch")
class ItemReportViewSet(viewsets.ModelViewSet):
    queryset = ItemReport.objects.select_related("category", "created_by").all()
    serializer_class = ItemReportSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    search_fields = ["title", "description", "location"]
    ordering_fields = ["created_at", "date_occurred", "title"]
    filterset_fields = ["report_type", "status", "category"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        cache.clear()

    def perform_update(self, serializer):
        obj = self.get_object()
        if obj.created_by_id != self.request.user.id and not self.request.user.is_staff:
            raise PermissionDenied("You can only edit your own report.")
        serializer.save()
        cache.clear()

    def perform_destroy(self, instance):
        if instance.created_by_id != self.request.user.id and not self.request.user.is_staff:
            raise PermissionDenied("You can only delete your own report.")
        instance.delete()
        cache.clear()

class ClaimRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ClaimRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        return (ClaimRequest.objects.select_related("item", "requester")
                .filter(requester=user) | ClaimRequest.objects.select_related("item", "requester")
                .filter(item__created_by=user)).distinct()

    def perform_create(self, serializer):
        item = serializer.validated_data["item"]
        if item.created_by_id == self.request.user.id:
            raise PermissionDenied("You cannot claim your own report.")
        if item.status != ItemReport.Status.OPEN:
            raise PermissionDenied("This report is not open for claims.")
        if ClaimRequest.objects.filter(item=item, requester=self.request.user).exists():
            raise PermissionDenied("You already submitted a claim for this report.")
        serializer.save(requester=self.request.user)
        cache.clear()
