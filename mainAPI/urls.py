from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from mainAPI.views import menuItemsView, menuItemView, userGroupsView

urlpatterns = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('menu-items/<int:pk>', menuItemView.as_view()),
    path('menu-items', menuItemsView.as_view()),
    path('groups', userGroupsView.as_view()),

]