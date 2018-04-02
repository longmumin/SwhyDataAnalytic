from rest_framework import serializers
from .models import loadUserDataModel

class loadUserDataSerializer(serializers.ModelSerializer):
    userData = serializers.JSONField()

    class Meta:
        model = loadUserDataModel
        fields = ('userData',)


