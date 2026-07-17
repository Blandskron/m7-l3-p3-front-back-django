from django.contrib import admin
from .models import MemberProfile


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "membership_id", "joined_at")
    list_select_related = ("user",)
    search_fields = ("user__username", "membership_id")
