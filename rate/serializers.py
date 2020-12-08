from rest_framework import serializers
from .models import Price, Port


class PriceSerializer(serializers.ModelSerializer):
    """
    Price Serializer
    """
    average_price = serializers.IntegerField(read_only=True)
    day = serializers.DateField(format="%Y-%m-%d", input_formats=['%Y-%m-%d'])
    orig_code = serializers.PrimaryKeyRelatedField(label='test', queryset=Port.objects.all(), write_only=True)
    dest_code = serializers.PrimaryKeyRelatedField(queryset=Port.objects.all(), write_only=True)
    price = serializers.IntegerField(write_only=True)

    class Meta:
        model = Price
        fields = ['day', 'orig_code', 'dest_code', 'price', 'average_price']
