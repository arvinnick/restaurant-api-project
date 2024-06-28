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
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
