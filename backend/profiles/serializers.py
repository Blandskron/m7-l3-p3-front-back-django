from rest_framework import serializers

from .models import MemberProfile


class MemberProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = MemberProfile
        fields = [
            "id", "user", "username", "membership_id", "address", "phone", "joined_at"
        ]
        read_only_fields = ["joined_at"]
