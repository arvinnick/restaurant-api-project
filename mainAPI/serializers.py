from rest_framework import serializers
from django.contrib.auth.models import User

from mainAPI.models import menu_items


class MenuItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = menu_items

class userGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
