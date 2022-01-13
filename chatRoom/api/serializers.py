from django.db.models import fields
from rest_framework.serializers import ModelSerializer
from chatRoom.models import Room


class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'