from django.contrib.auth.models import Group, User
from django.shortcuts import render, get_list_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from mainAPI.models import MenuItem, Cart, Category
from mainAPI.serializers import MenuItemsSerializer, UserSerializer, CartSerializer


# Create your views here.

class MenuItemView(ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemsSerializer

    def create(self, request, *args, **kwargs):
        serializer = MenuItemsSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            obj = MenuItem()
            obj.price = serializer.validated_data['price']
            obj.category = serializer.validated_data['category']
            obj.featured = serializer.validated_data['featured']
            obj.title = serializer.validated_data['title']
            obj.save()
            serialized_obj = MenuItemsSerializer(obj)
            return Response(serialized_obj.data, status=status.HTTP_201_CREATED)
        except ValidationError as v_e:
            if v_e.args[0].get("category")[0].code == "does_not_exist":
                return Response({"error": "Category does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                raise v_e

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        else:
            return [IsAuthenticated()]


class SingleMenuItemView(RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemsSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        else:
            return [IsAuthenticated()]


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_groups(request, group):
    users = get_list_or_404(Group, name=group)
    serialized_users = UserSerializer(users)
    return Response(serialized_users.data, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def single_user(request, group, user_id):
    serialized_user = UserSerializer(user_id)
    if serialized_user.is_valid():
        if request.method == "GET":
            user = User.objects.get(pk=user_id)
            serialized_users = UserSerializer(user)
            return Response(serialized_users.data, status=status.HTTP_200_OK)
        elif request.method == "POST":
            if User.objects.exists(user_id):
                return Response(status=status.HTTP_409_CONFLICT, headers={"message": "User already exists"})
            else:
                user = User.objects.create_user(serialized_user.data.get("username"),
                                                serialized_user.data.get("email"),
                                                serialized_user.data.get("password"),
                                                group=group)
                user.save()
                return Response(user, status=status.HTTP_201_CREATED)


class UserView(ListCreateAPIView):
    queryset = User.objects.filter()
    serializer_class = UserSerializer


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def cart_menu_item(request):
    serializer = CartSerializer(data=request.data, many=True)
    if request.method == "GET":
        queryset = Cart.objects.all().filter(user=request.user)
        serialized_cart = CartSerializer(queryset, many=True)
        return Response(serialized_cart.data, status=status.HTTP_200_OK)
    elif request.method == "POST":
        if serializer.is_valid():
            menu_query = MenuItem.objects.filter(title=serializer.data.get('title'))
            v_data = serializer.validated_data
            obj = serializer.create(v_data)
            obj.unit_price = menu_query.get("price")
            obj.price = obj.unit_price * obj.quantity
            obj.save()
            return Response(obj.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        objs = Cart.objects.all().delete()
        objs.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
