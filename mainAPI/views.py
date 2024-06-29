from django.contrib.auth.models import Group, User
from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.views.generic import RedirectView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from mainAPI.models import MenuItem, Cart, Category, Order, OrderItem
from mainAPI.serializers import MenuItemsSerializer, UserSerializer, CartSerializer, OrderSerializer


# Create your views here.


@api_view(["GET", "POST", "PUT", "DELETE", "PATCH"])
@permission_classes([IsAuthenticated])
def menu_items_view(request):
    if request.method == "POST":
        if request.user.groups.filter(name='manager').exists():
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
                raise v_e
        else:
            return Response({"user not authorized"}, status=status.HTTP_403_FORBIDDEN)
    elif request.method == "GET":
        obj = MenuItem.objects.all()
        serialized_obj = MenuItemsSerializer(obj, many=True)
        return Response(serialized_obj.data, status=status.HTTP_200_OK)
    else:
        if request.user.groups.filter(name='manager').exists():
            return Response({"method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            return Response({"user not authorized"}, status=status.HTTP_403_FORBIDDEN)


class SingleMenuItemView(RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemsSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        else:
            return [IsAuthenticated()]


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def user_groups(request, group):
    if group == 'delivery-crew':
        group = "delivery crew"
    try:
        users = Group.objects.get(name=group)
        user_set = users.user_set.all()
    except Group.DoesNotExist:
        return Response("check the URL", status=status.HTTP_400_BAD_REQUEST)
    if request.user.groups.filter(name='manager').exists():
        if request.method == "GET":
            serialized_users = UserSerializer(user_set, many=True, fields=("username", "email"))
            return Response(serialized_users.data, status=status.HTTP_200_OK)
        elif request.method == "POST":
            try:
                user_set.create(username=request.data.get('username'),
                                is_staff=True,
                                is_active=True,
                                password=request.data.get('password'),
                                email=request.data.get('email'))
            # user_set.save()
            # serialized_users = UserSerializer(user_set, many=True)
                return Response(status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                if User.objects.filter(username=request.data.get('username')).exists():
                    obj = User.objects.filter(username=request.data.get('username'))
                    users.user_set.add(obj.get().id)
                    return Response(status=status.HTTP_201_CREATED)
                else:
                    raise e
        elif request.method == "DELETE":
            user_set.create(username=request.data.get('username'),
                            is_staff=True,
                            is_active=True,
                            password=request.data.get('password'),
                            email=request.data.get('email'))
            user_set.save()
            # serialized_users = UserSerializer(user_set, many=True)
            return Response(status=status.HTTP_201_CREATED)
    else:
        return Response({"message": "user not authorized"}, status=status.HTTP_401_UNAUTHORIZED)
    # else:
    #     return Response(serialized_users.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def single_user(request, user_id, group=None):
    serialized_user = UserSerializer(user_id)
    if serialized_user.is_valid():
        if request.method == "GET":
            user = User.objects.get()
            serialized_users = UserSerializer(user)
            return Response(serialized_users.data, status=status.HTTP_200_OK)
        elif request.method == "POST":
            if User.objects.exists(user_id):
                return Response(status=status.HTTP_409_CONFLICT, headers={"message": "User already exists"})
            else:
                user = User.objects.create_user(serialized_user.data.get(),
                                                serialized_user.data.get(),
                                                serialized_user.data.get(),
                                                group=serialized_user.data.get() if group else "customer")
                user.save()
                return Response(user, status=status.HTTP_201_CREATED)


@api_view(["POST", "GET"])
def user_view_me(request):
    if request.method == "POST":
        user_name = request.data.get("username")
        password = request.data.get("password")
        user = User.objects.get(username=user_name)
        if user is None:
            user = User.objects.create_user(username=user_name, password=password)
            costumer_group = Group.objects.get(name="customer")
            costumer_group.user_set.add(user)
            user.save()
            data = UserSerializer(user).data
            data.pop("password")
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response("user already exists", status=status.HTTP_409_CONFLICT)
    elif request.method == "GET":
        if request.user.is_authenticated:
            user_name = request.user.username
            try:
                user = get_object_or_404(User, username=user_name)
            except Http404:
                return Response(Http404(), status=status.HTTP_404_NOT_FOUND)
            data = UserSerializer(user).data
            data.pop("password")
            data["email"] = user.email
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "user not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({"message": "{} not allowed".format(request.method)}, status=status.HTTP_400_BAD_REQUEST)


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
            menu_query = MenuItem.objects.filter(title=serializer.data.get())
            v_data = serializer.validated_data
            obj = serializer.create(v_data)
            obj.unit_price = menu_query.get()
            obj.price = obj.unit_price * obj.quantity
            obj.user = request.user
            obj.save()
            return Response(obj.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        objs = Cart.objects.all().filter(user=request.user).delete()
        objs.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class OrderView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get(self, request, **kwargs):
        if "customer" in list(self.request.user.groups.values_list("name", flat=True)):
            data = self.queryset.filter(user=self.request.user)
        elif "manager" in list(self.request.user.groups.values_list("name", flat=True)):
            data = self.queryset
        elif "delivery crew" in list(self.request.user.groups.values_list("name", flat=True)):
            data = self.queryset.filter(delivery_crew=self.request.user)
        else:
            return Response({"message": "you should login to access orders"},
                            status=status.HTTP_401_UNAUTHORIZED)

        serialized_data = self.serializer_class(data)
        return Response(serialized_data.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        if self.request.user.groups == "customer":
            queryset = Cart.objects.filter(user=self.request.user)
            serializer = CartSerializer(queryset, many=True)
            order_data = Order()
            for key, value in serializer.data.items:
                pass
