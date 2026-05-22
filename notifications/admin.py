from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "channel", "template", "status", "created_at")
    list_filter = ("channel", "status")

# Register your models here.
