from django.urls import path
from django.contrib.auth.views import LogoutView
from .apps import UsersConfig
from .views import UserLoginView, RegisterView, email_verification_view, \
    PasswordRecoveryView, UserListView, toggle_user_block

app_name = UsersConfig.name

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='mailing:home'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/<str:token>/', email_verification_view, name='verify_email'),
    path('recovery/', PasswordRecoveryView.as_view(), name='recovery'),
# Управление пользователями (для Менеджера)
    path('users-list/', UserListView.as_view(), name='user_list'),
    path('users-list/<int:pk>/toggle-block/', toggle_user_block, name='toggle_block'),
]
