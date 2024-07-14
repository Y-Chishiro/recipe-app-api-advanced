"""
URL mappings for the user API.
"""
from django.urls import path

from user import views


# test_user_api.pyで
# # CREATE_USER_URL = reverse('user:create')
# と書いた。ここのuserに当たるのがアプリ名で、createがAPI名。らしい。
app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
]
