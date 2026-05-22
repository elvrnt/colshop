from django.urls import include, path
from rest_framework import routers
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt

from .views import (
    ProductViewSet,
    CampaignViewSet,
    ParticipationViewSet,
    PaymentIntentViewSet,
    RegisterView,
    MeView,
    LoginView,
)
from .schema import schema

router = routers.DefaultRouter()
router.register(r"products", ProductViewSet)
router.register(r"campaigns", CampaignViewSet)
router.register(r"participations", ParticipationViewSet, basename="participations")
router.register(r"payments", PaymentIntentViewSet)

urlpatterns = [
    path("rest/", include(router.urls)),
    path("rest/auth/login/", LoginView.as_view(), name="api-token-auth"),
    path("rest/auth/register/", RegisterView.as_view(), name="api-register"),
    path("rest/me/", MeView.as_view(), name="api-me"),
    path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
]

