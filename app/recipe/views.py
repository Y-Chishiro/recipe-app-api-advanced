"""
Views for the recipe APIs
"""
from rest_framework import (
    viewsets,
    mixins, # 92
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Recipe,
    Tag, # 92
    Ingredient, # 107
)
from recipe import serializers


# ModelViewsetはとりわけModelとの連動を強化した親クラス。
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    # serializer_class = serializers.RecipeSerializer
    serializer_class = serializers.RecipeDetailSerializer # Detailの方がCRUD全てを使うので、RecipeSerializerではなくこちらをデフォルトにする
    queryset = Recipe.objects.all() # querysetはこのViewSetの中で触れるObjectのリスト
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Overrideする。list取得用...ではない！
    # これは実はdetailの時も呼び出されるが、その場合はget_querysetが呼び出された後に、DRFの内部でpk=pkのオブジェクトが呼び出されている。分かりづらい。。。
    # Claude先生様様。https://claude.ai/chat/3924e0c9-6f5a-42b5-8700-10dd9eb32643
    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id') # ちゃんと手でロジックをかませている。。

    # detail取得用
    def get_serializer_class(self):
        """Return teh sereializer class for request."""
        if self.action == 'list': # これはurlを見て、recipes/などでアクセスすると、勝手にaction属性にlistをつけてくれるらしい。。
            return serializers.RecipeSerializer

        return self.serializer_class

    # 85: implement create api
    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user) # ユーザはこちらで追加することにより、ユーザ側でのPOST時にユーザIDを含める必要がなくなる。

# 92 Implement tag listing API
class TagViewSet(mixins.DestroyModelMixin, # 96はこの1行だけ追加
                 mixins.UpdateModelMixin, # 94はこの1行だけ追加
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')


# 107 Implement ingredient listing API
class IngredientViewSet(mixins.DestroyModelMixin, # 111 Implement delete ingredient API
                        mixins.UpdateModelMixin, # 109 Implement update ingredient API
                        mixins.ListModelMixin, # 107
                        viewsets.GenericViewSet): # 107
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')


