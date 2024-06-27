from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from mainAPI.views import MenuItemView, SingleMenuItemView, UserView, user_groups, single_user, cart_menu_item

urlpatterns = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('menu-items/', MenuItemView.as_view(), name='menu_item'),
    path('menu-items/<int:pk>', SingleMenuItemView.as_view(), name='menu_item'),
    path('groups/<str:group>/users/', user_groups, name='group'),
    path('groups/<str:group>/users/<int:user_id>', single_user, name='group'),
    path('users/', UserView.as_view(), name='users'),
    path('cart/menu-items', cart_menu_item, name="cart")

]