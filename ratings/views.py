from rest_hooks.models import Hook
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Invite, Rating
from .serializers import (InviteSerializer, RatingSerializer, HookSerializer)


class HookViewSet(viewsets.ModelViewSet):
    """
    Retrieve, create, update or destroy webhooks.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Hook.objects.all()
    serializer_class = HookSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class InviteViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows dummy models to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Invite.objects.all()
    serializer_class = InviteSerializer
    filter_fields = ('identity', 'version', 'invited', 'completed',
                     'expired', 'expires_at', 'created_at', 'updated_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user,
                        updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class RatingViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows dummy models to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    filter_fields = ('identity', 'invite', 'version', 'question_id',
                     'created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user,
                        updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
