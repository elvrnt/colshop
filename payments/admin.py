from django.contrib import admin
from .models import PaymentIntent


@admin.register(PaymentIntent)
class PaymentIntentAdmin(admin.ModelAdmin):
    list_display = ("id", "participation", "provider", "status", "amount")
    list_filter = ("status", "provider")
    search_fields = ("idempotency_key",)

# Register your models here.
