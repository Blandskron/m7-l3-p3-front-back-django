from rest_framework.routers import DefaultRouter

from .views import MemberProfileViewSet

router = DefaultRouter()
router.register("profiles", MemberProfileViewSet, basename="profiles")

urlpatterns = router.urls
