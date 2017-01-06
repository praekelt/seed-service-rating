from django.contrib import admin

from .models import Rating, Invite


class InviteAdmin(admin.ModelAdmin):
    list_display = ("id", "identity", "invited", "completed", "expired",
                    "invites_sent", "send_after", "expires_at", "created_at",
                    "updated_at", "created_by", "updated_by",)
    list_filter = ("invited", "completed", "expired", "invites_sent",
                   "send_after", "expires_at", "created_at", "updated_at",)
    search_fields = ["id", "identity"]


class RatingAdmin(admin.ModelAdmin):
    list_display = ("id", "identity", "invite", "question_id", "created_at",
                    "updated_at", "created_by", "updated_by",)
    list_filter = ("question_id", "created_at", "updated_at",)
    search_fields = ["id", "identity", "invite__id"]


admin.site.register(Invite, InviteAdmin)
admin.site.register(Rating, RatingAdmin)
