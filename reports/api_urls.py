from rest_framework.routers import DefaultRouter
from .api_views import CategoryViewSet, ItemReportViewSet, ClaimRequestViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="api-category")
router.register("reports", ItemReportViewSet, basename="api-report")
router.register("claims", ClaimRequestViewSet, basename="api-claim")
urlpatterns = router.urls
