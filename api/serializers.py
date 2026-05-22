from django.contrib.auth import get_user_model
from django.db.models import Sum, F, DecimalField
from rest_framework import serializers

from catalog.models import Product
from campaigns.models import Campaign, Participation
from payments.models import PaymentIntent


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email")


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class CampaignSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )
    total_quantity = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = (
            "id",
            "title",
            "description",
            "product",
            "product_id",
            "organizer",
            "target_quantity",
            "min_quantity",
            "max_quantity",
            "deadline",
            "pricing_rules",
            "status",
            "created_at",
            "updated_at",
            "total_quantity",
            "total_amount",
            "participants",
        )
        read_only_fields = ("status", "created_at", "updated_at")

    def get_total_quantity(self, obj: Campaign):
        return (
            Participation.objects.filter(campaign=obj)
            .exclude(status=Participation.Status.CANCELLED)
            .aggregate(total=Sum("quantity"))
            .get("total")
            or 0
        )

    def get_total_amount(self, obj: Campaign):
        return (
            Participation.objects.filter(campaign=obj)
            .exclude(status=Participation.Status.CANCELLED)
            .aggregate(
                total=Sum(
                    F("amount"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
            .get("total")
            or 0
        )

    def get_participants(self, obj: Campaign):
        qs = (
            Participation.objects.select_related("user")
            .filter(campaign=obj)
            .exclude(status=Participation.Status.CANCELLED)
        )
        return ParticipationBriefSerializer(qs, many=True).data


class ParticipationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    campaign = CampaignSerializer(read_only=True)
    campaign_id = serializers.PrimaryKeyRelatedField(
        queryset=Campaign.objects.all(), source="campaign", write_only=True
    )

    class Meta:
        model = Participation
        fields = (
            "id",
            "campaign",
            "campaign_id",
            "user",
            "quantity",
            "amount",
            "status",
            "created_at",
        )
        read_only_fields = ("status", "created_at")

    def validate(self, attrs):
        campaign: Campaign = attrs["campaign"]
        qty = attrs.get("quantity", 1)
        if qty < campaign.min_quantity:
            raise serializers.ValidationError("Quantity below campaign minimum")
        if campaign.max_quantity and qty > campaign.max_quantity:
            raise serializers.ValidationError("Quantity above campaign maximum")
        return attrs


class ParticipationBriefSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Participation
        fields = ("id", "user", "quantity", "amount", "status", "created_at")


class PaymentIntentSerializer(serializers.ModelSerializer):
    participation = ParticipationSerializer(read_only=True)
    participation_id = serializers.PrimaryKeyRelatedField(
        queryset=Participation.objects.all(), source="participation", write_only=True
    )

    class Meta:
        model = PaymentIntent
        fields = (
            "id",
            "participation",
            "participation_id",
            "provider",
            "status",
            "idempotency_key",
            "amount",
            "payload",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("status", "created_at", "updated_at")

