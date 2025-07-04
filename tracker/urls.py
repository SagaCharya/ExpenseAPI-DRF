from django.urls import path
from .views import register_user, CustomTokenObtainPairView, expense_list, expense_detail
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('auth/register/', register_user, name='register_user'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('expense/', expense_list, name='expense_list'),
    path('expense/<int:pk>/', expense_detail, name='expense_detail'),
]