from rest_framework import serializers

from .models import Interaction, MessageSent


class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = '__all__'
        

class MessageSentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageSent
        fields = '__all__'