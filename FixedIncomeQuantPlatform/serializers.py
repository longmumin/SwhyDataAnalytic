from rest_framework import serializers
from .models import loadDataModel


class loadDataSerializer(serializers.ModelSerializer):
    quoteData = serializers.JSONField()
    class Meta:
        model = loadDataModel
        fields = ('bondType', 'containerName', 'method', 'quoteData')
