from rest_framework import serializers

from .models import SeleneModel, SeleneNode


class SeleneModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeleneModel
        fields = '__all__'
        
        
class SeleneNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeleneNode
        fields = '__all__'