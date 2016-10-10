from .models import Invite, Rating
from rest_hooks.models import Hook
from rest_framework import serializers


class InviteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Invite
        read_only_fields = ('created_by', 'updated_by')
        fields = ('id', 'identity', 'version', 'invited', 'completed',
                  'expired', 'invite', 'expires_at', 'created_at',
                  'updated_at')


class RatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rating
        read_only_fields = ('created_by', 'updated_by')
        fields = ('id', 'identity', 'invite', 'version', 'question_id',
                  'question_text', 'answer_text', 'answer_value', 'created_at')


class CreateUserSerializer(serializers.Serializer):
    email = serializers.EmailField()


class HookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hook
        read_only_fields = ('user',)
