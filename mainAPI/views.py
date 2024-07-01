import datetime

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
from mainAPI.serializers import MenuItemsSerializer, UserSerializer, CartSerializer, OrderSerializer, \
    OrderItemSerializer


# Create your views here.


@api_view(["GET", "POST", "PUT", "DELETE", "PATCH"])
@permission_classes([IsAuthenticated])
def menuitems(request):
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
        obj = MenuItem.objects.select_related('category').all()
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


@api_view(["GET", "POST"])
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
    else:
        return Response({"message": "user not authorized"}, status=status.HTTP_401_UNAUTHORIZED)
    # else:
    #     return Response(serialized_users.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def single_user(request, user_id, group=None):
    if group == 'delivery-crew':
        group = "delivery crew"
    try:
        users = Group.objects.get(name=group)
        user_set = users.user_set
    except Group.DoesNotExist:
        return Response("check the URL", status=status.HTTP_400_BAD_REQUEST)
    if request.user.groups.filter(name='manager').exists():
        if User.objects.filter(id=user_id).exists():
            user_set.remove(user_id)
            return Response(status=status.HTTP_200_OK, headers={"message": "User already exists"})
        else:
            return Response("user not found", status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


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
    queryset = Cart.objects.all().filter(user=request.user).all()
    if request.method == "GET":
        serialized_cart = CartSerializer(queryset, many=True)
        return Response(serialized_cart.data, status=status.HTTP_200_OK)
    elif request.method == "POST":
        menu_item = MenuItem.objects.filter(title=request.data.get('title')).get()
        quantity = eval(request.data.get('quantity'))
        try:
            cart_item = Cart()
            cart_item.user = request.user
            cart_item.menuitem = menu_item
            cart_item.unit_price = cart_item.menuitem.price
            cart_item.quantity = quantity
            cart_item.price = cart_item.unit_price * cart_item.quantity
            cart_item.save()
        except IntegrityError as ie:
            if Cart.objects.filter(menuitem=menu_item).exists():
                cart_item = Cart.objects.filter(menuitem=menu_item).get()
                cart_item.quantity += quantity
                cart_item.price = cart_item.unit_price * cart_item.quantity
                cart_item.save()
            else:
                raise ie
        return Response(status=status.HTTP_201_CREATED)
    elif request.method == "DELETE":
        objs = Cart.objects.all().filter(user=request.user).delete()
        # objs.save()
        return Response(status=status.HTTP_202_ACCEPTED)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

class OrderView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        return [IsAuthenticated()]
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
        if data.exists():
            serialized_data = self.serializer_class(data)
            return Response(serialized_data.data, status=status.HTTP_200_OK)
        else:
            return Response("no order", status=status.HTTP_404_NOT_FOUND)


    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        group = user.groups.get()
        if group.name == "customer":
            cart = Cart.objects.filter(user=user)
            cart_serializer = CartSerializer(cart, many=True)
            order = Order.objects.filter(user=user)
            if not order.exists():
                order = Order.objects.create(user=user, date=str(datetime.today().date()), total=0)
            for data in cart_serializer.data:
                OrderItem.objects.create(order=order, quantity=data['quantity'],
                                         menuItem=MenuItem.objects.get(title=data['menuitem']),
                                         unit_price=data['unit_price'], price=data['price'])
            cart.all().delete()
            order.save()
            return Response(status=status.HTTP_201_CREATED)

