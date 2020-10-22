from rest_framework import serializers
from engine import models


class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Products
        fields = ('id', 'production_date', 'name', 'price')
        write_only_fields = ('price',)


class OrderSerializer(serializers.ModelSerializer):
    product = ProductsSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = models.Order
        fields = ('id', 'created_at', 'updated_at', 'status', 'product', 'product_id', 'is_discounted', 'total_price')
        read_only_fields = ('created_at', 'updated_at', 'is_discounted', 'total_price')
