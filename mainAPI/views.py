from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from .models import menu_items
from . import serializers


# Create your views here.
class menuItemsView(ListCreateAPIView):
    querysets = menu_items.objects.all()
    serializer_class = serializers.MenuItemsSerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated()]
        return [permission for permission in permission_classes]

class menuItemView(RetrieveUpdateDestroyAPIView, CreateAPIView):
    querysets = menu_items.objects.all()
    serializer_class = serializers.MenuItemsSerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated()]
        return [permission for permission in permission_classes]


class userGroupsView(ListAPIView):
    serializer_class = serializers.userGroupSerializer
    queryset = User.objects.all()