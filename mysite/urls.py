from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

urlpatterns = [
    path('api/token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

    path('api/auth/register/', views.RegisterView.as_view(), name='register'),
    path('api/auth/login/', views.LoginView.as_view(), name='login'),
    path('api/auth/logout/', views.LogoutView.as_view(),name='logout'),
    path('api/user/profile/',views.UserProfileView.as_view(),name='profile'),
    path('api/user/change-password/',views.ChangePasswordView.as_view(),name='change_password'),

    path('',views.home_page, name='home'),
    path('login/',views.login_page, name='login_page'),
]
