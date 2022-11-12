from rest_framework import serializers

from .models import SeleneModel, SeleneNode


class SeleneModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeleneModel
        fields = '__all__'
        read_only_fields = ('created_at',)
        
        
class SeleneNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeleneNode
        fields = '__all__'
        read_only_fields = ('created_at',)