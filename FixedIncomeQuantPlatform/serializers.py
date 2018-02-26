from rest_framework import serializers
from .models import loadDataModel

class loadDataSerializer(serializers.ModelSerializer):
    quoteData = serializers.JSONField()

    class Meta:
        model = loadDataModel
        fields = ('bondType', 'containerName', 'method', 'quoteData')

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

# class diffDataSerializer(serializers.Serializer):
#     diffData = serializers.JSONField()
#
#     class Meta:
#         model = diffDataModel
#         fields = ('diffData')
#
# class bondYTMDiffSerializer(serializers.ModelSerializer):
#     #quoteData = diffDataSerializer(many=True)
#     quoteData = serializers.JSONField()
#
#     class Meta:
#         model = bondYTMDiffModel
#         fields = ('bondType', 'containerName', 'method', 'quoteData')

#

