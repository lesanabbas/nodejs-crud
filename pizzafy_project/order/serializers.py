from rest_framework import serializers
from .models import Order, OrderLine, Checkout, CheckoutLine

class CheckoutLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckoutLine
        fields = ['id', 'pizza', 'quantity', 'price', 'size', 'customizations']

class CheckoutSerializer(serializers.ModelSerializer):
    checkout_lines = CheckoutLineSerializer(many=True)  # Nested serializer for checkout lines

    class Meta:
        model = Checkout
        fields = ['id', 'user', 'shipping_address', 'billing_address', 'total_price', 'checkout_lines']
        
        
class OrderLineSerializer(serializers.ModelSerializer):
    pizza_name = serializers.CharField(source='pizza.name', read_only=True)

    class Meta:
        model = OrderLine
        fields = ['id', 'pizza', 'pizza_name', 'quantity']
        

class OrderSerializer(serializers.ModelSerializer):
    order_lines = OrderLineSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    delivery_partner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'created_at', 'delivery_partner', 'order_lines']