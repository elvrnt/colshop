from django.db import models
from campaigns.models import Participation


class PaymentIntent(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        AUTHORIZED = "authorized", "Authorized"
        CAPTURED = "captured", "Captured"
        FAILED = "failed", "Failed"

    participation = models.OneToOneField(Participation, on_delete=models.CASCADE, related_name="payment_intent")
    provider = models.CharField(max_length=50, default="mock")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    idempotency_key = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.provider}:{self.idempotency_key}"

# Create your models here.
