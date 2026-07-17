from rest_framework import viewsets

from .models import MemberProfile
from .serializers import MemberProfileSerializer


class MemberProfileViewSet(viewsets.ModelViewSet):
    """Demuestra la relación uno a uno entre usuario y perfil de socio."""

    queryset = MemberProfile.objects.select_related("user").order_by("id")
    serializer_class = MemberProfileSerializer
