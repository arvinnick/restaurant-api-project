from django.contrib.auth.models import Group, User

from rest_framework import serializers

from mainAPI.models import MenuItem, Cart, Order


class MenuItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title','featured' , 'price', 'category']


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity']

    def create(self, validated_data):
        return Cart(**validated_data)

    def delete(self, validated_data):
        res = Cart.objects.all().delete()
        return res



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
