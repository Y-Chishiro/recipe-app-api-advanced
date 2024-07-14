"""
Views for the user API.
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


# user:create
class CreateUserView(generics.CreateAPIView): # おそらくここでCreateAPIViewを指定しているので、Createしか受け付けない。
    """Create a new user in the system."""
    serializer_class = UserSerializer # そのため、ここでUserSerializerを指定すると、自動的にcreateメソッドが指定される。


# user:token
class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES # ここはオプションらしい?


# user:me
class ManageUserView(generics.RetrieveUpdateAPIView): # その名の通り、retrive（取得）とUpdate（更新）に特化したAPIViewクラス。
    """Manage the authenticated user."""
    serializer_class = UserSerializer # 同じシリアライザを使い回す
    authentication_classes = [authentication.TokenAuthentication] # どのようにユーザを知るか？方法の指定。
    permission_classes = [permissions.IsAuthenticated] # 認証されたユーザのみ使えるAPIである、ということ。

    # GETリクエストのメソッドをオーバーライド
    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user # 認証されたユーザはself.requestにアサインされているので、それをそのまま使う。
