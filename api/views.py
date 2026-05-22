from django.contrib.auth import authenticate, get_user_model
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import BasicAuthentication, TokenAuthentication

from catalog.models import Product
from campaigns.models import Campaign, Participation
from payments.models import PaymentIntent
from .serializers import (
    ProductSerializer,
    CampaignSerializer,
    ParticipationSerializer,
    PaymentIntentSerializer,
    UserSerializer,
)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # no CSRF/session requirement

    def post(self, request):
        User = get_user_model()
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email", "")
        if not username or not password:
            return Response({"detail": "username and password required"}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({"detail": "username already exists"}, status=400)
        user = User.objects.create_user(username=username, password=password, email=email)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data}, status=201)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # no CSRF/session requirement

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication, BasicAuthentication]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    search_fields = ["title"]


class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.select_related("product", "organizer").all()
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ["status"]
    search_fields = ["title", "description", "product__title"]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def join(self, request, pk=None):
        campaign = self.get_object()
        quantity = int(request.data.get("quantity", 1))
        amount = quantity * campaign.product.price
        participation, created = Participation.objects.get_or_create(
            campaign=campaign,
            user=request.user,
            defaults={"quantity": quantity, "amount": amount},
        )
        if not created:
            participation.quantity = quantity
            participation.amount = amount
            participation.status = Participation.Status.PENDING
            participation.save(update_fields=["quantity", "amount", "status", "updated_at"])
        serializer = ParticipationSerializer(participation, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def participants(self, request, pk=None):
        campaign = self.get_object()
        qs = campaign.participations.select_related("user").exclude(status=Participation.Status.CANCELLED)
        data = ParticipationSerializer(qs, many=True, context={"request": request}).data
        return Response(data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated], url_path="leave")
    def leave(self, request, pk=None):
        campaign = self.get_object()
        try:
            participation = Participation.objects.get(campaign=campaign, user=request.user)
        except Participation.DoesNotExist:
            return Response({"detail": "Not participating"}, status=status.HTTP_404_NOT_FOUND)
        participation.status = Participation.Status.CANCELLED
        participation.save(update_fields=["status", "updated_at"])
        return Response({"detail": "Participation cancelled"})

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated], url_path="stop")
    def stop(self, request, pk=None):
        campaign = self.get_object()
        user = request.user
        if not (user.is_staff or campaign.organizer_id == user.id):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        campaign.status = Campaign.Status.CLOSED
        campaign.save(update_fields=["status", "updated_at"])
        return Response({"detail": "Campaign closed"})


class ParticipationViewSet(viewsets.ModelViewSet):
    serializer_class = ParticipationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Participation.objects.select_related("campaign", "user").filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated], url_path="cancel")
    def cancel(self, request, pk=None):
        participation = self.get_object()
        user = request.user
        is_owner = participation.user_id == user.id
        is_organizer = participation.campaign.organizer_id == user.id
        if not (is_owner or is_organizer or user.is_staff):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        participation.status = Participation.Status.CANCELLED
        participation.save(update_fields=["status", "updated_at"])
        return Response({"detail": "Participation cancelled"})


class PaymentIntentViewSet(viewsets.ModelViewSet):
    queryset = PaymentIntent.objects.select_related("participation").all()
    serializer_class = PaymentIntentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

# Create your views here.
