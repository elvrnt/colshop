from django.contrib import admin
from .models import Campaign, Participation


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("title", "product", "organizer", "status", "deadline")
    list_filter = ("status",)
    search_fields = ("title", "product__title", "organizer__username")


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ("campaign", "user", "quantity", "amount", "status")
    list_filter = ("status",)

# Register your models here.
