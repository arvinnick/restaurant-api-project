from django.db import models
from rest_framework.generics import ListAPIView
from . import serializers
# Create your models here.
class menu_items(ListAPIView):
    querysets = []
    serializer = serializers.MenuItemsSerializer
