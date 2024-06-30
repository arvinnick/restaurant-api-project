from django.contrib.auth.models import Group, User

from rest_framework import serializers

from mainAPI.models import MenuItem, Cart, Order, Category


class MenuItemsSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = MenuItem
        fields = ['title', 'featured', 'price', 'category']


class CartItemsSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(decimal_places=2, max_digits=2)
    menuitem = MenuItemsSerializer()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemsSerializer(many=True, read_only=True)
    price = serializers.SerializerMethodField(method_name="calculate_total_price")
    class Meta:
        model = Cart
        fields = ['items', 'price']
        depth = 1

    def calculate_total_price(self, cart):
        total_price = 0
        total_price += cart.price * cart.quantity
        return total_price

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status", "total"]


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
