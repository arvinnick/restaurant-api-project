from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from mainAPI.views import SingleMenuItemView, user_groups, single_user, cart_menu_item, \
    OrderView, user_view_me, menuitems

urlpatterns = [
    path('/menu-items', menuitems, name='menuitem-detail'),
    path('/menu-items/<int:pk>', SingleMenuItemView.as_view(), name='menuitem-detail'),
    path('/groups/<str:group>/users', user_groups, name='group'),
        path('/groups/<str:group>/users/<int:user_id>', single_user, name='group'),
    path('/users', user_view_me, name='users'),
    path('/cart/menu-items', cart_menu_item, name="cart"),
    path('/orders', OrderView.as_view(), name='orders'),
]