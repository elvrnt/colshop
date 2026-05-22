import graphene
from graphene_django import DjangoObjectType

from catalog.models import Product
from campaigns.models import Campaign, Participation


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "title", "description", "price", "attributes", "created_at")


class CampaignType(DjangoObjectType):
    class Meta:
        model = Campaign
        fields = (
            "id",
            "title",
            "description",
            "product",
            "organizer",
            "target_quantity",
            "min_quantity",
            "max_quantity",
            "deadline",
            "pricing_rules",
            "status",
        )


class ParticipationType(DjangoObjectType):
    class Meta:
        model = Participation
        fields = ("id", "campaign", "user", "quantity", "amount", "status", "created_at")


class Query(graphene.ObjectType):
    products = graphene.List(ProductType)
    campaigns = graphene.List(CampaignType, status=graphene.String(required=False))
    participations = graphene.List(ParticipationType)

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_campaigns(self, info, status=None):
        qs = Campaign.objects.select_related("product", "organizer")
        if status:
            qs = qs.filter(status=status)
        return qs

    def resolve_participations(self, info):
        user = info.context.user
        qs = Participation.objects.select_related("campaign", "user")
        if user.is_authenticated:
            return qs.filter(user=user)
        return qs.none()


schema = graphene.Schema(query=Query)

