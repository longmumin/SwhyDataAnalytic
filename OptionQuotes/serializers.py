from rest_framework import serializers
from .models import loadDataModel


class loadDataSerializer(serializers.ModelSerializer):
    quoteData = serializers.JSONField()

    class Meta:
        model = loadDataModel
        fields = ('qixian', 'quoteData')


class loadTDataSerializer(serializers.ModelSerializer):
    quoteData = serializers.JSONField()

    class Meta:
        model = loadDataModel
        fields = ('quoteData', 'forward', 'lastPrice')
#         fields = ('qixian', 'selected_date', 'instrument', 'futuresType', 'containerName', 'quoteData')


class bondYTMAnalyicDataSerializer(serializers.ModelSerializer):
    quoteData = serializers.JSONField()

    class Meta:
        model = loadDataModel
        fields = ('quoteData',)


class bondYTMMatrixSerializer(serializers.ModelSerializer):
    quoteData = serializers.JSONField()

    class Meta:
        model = loadDataModel
        fields = ('containerName', 'quoteData')