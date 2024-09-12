from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import CreateUserView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('create-user/', CreateUserView.as_view(), name='create-user'),
    path('delete-user/', views.DeleteUserView.as_view(), name='delete-user'),
    path('login/', views.LoginView.as_view(), name='login'),
]