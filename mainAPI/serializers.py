from datetime import datetime

from django.contrib.auth.models import Group, User

from rest_framework import serializers

from mainAPI.models import MenuItem, Cart, Order, Category, OrderItem


class MenuItemsSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = MenuItem
        fields = ['title', 'featured', 'price', 'category']


class CartSerializer(serializers.ModelSerializer):
    menuitem = serializers.StringRelatedField(read_only=True)
    price = serializers.SerializerMethodField(method_name="total_price")

    class Meta:
        model = Cart
        fields = ["quantity", "unit_price", "price", "menuitem"]

    def total_price(self, obj):
        return obj.quantity * obj.unit_price


class OrderSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField(method_name="get_total", default=0)
    date = serializers.DateField(format="%Y-%m-%d", default=str(datetime.today().date()))

    class Meta:
        model = Order
        fields = ["total", "date", "status", "delivery_crew"]

    def get_total(self, order):
        if order.exists():
            queryset = OrderItem.objects.filter(order=order.get())
            total = 0
            serializer_order_items = OrderItemSerializer(queryset, many=True)
            for order_item in serializer_order_items.data:
                total += order_item['price']
            return total
        else:
            return 0


from rest_framework import serializers
from mainAPI.models import OrderItem, MenuItem

class OrderItemSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField(method_name="total_price")
    menuItem = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["quantity", "unit_price", "menuItem", "price"]

    def total_price(self, obj):
        return obj.quantity * obj.unit_price

    def create(self, validated_data):
        menuItem = validated_data.get('menuItem')
        validated_data['unit_price'] = menuItem.price
        validated_data['price'] = validated_data['quantity'] * menuItem.price
        return OrderItem.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.menuItem = validated_data.get('menuItem', instance.menuItem)
        instance.unit_price = instance.menuItem.price
        instance.price = self.total_price(instance)
        instance.save()
        return instance


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password", "email"]

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
