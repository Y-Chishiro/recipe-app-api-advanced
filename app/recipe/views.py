"""
Views for the recipe APIs
"""
# 131 Implement recipe filter feature
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from rest_framework import (
    viewsets,
    mixins, # 92
    status, # 126
)
from rest_framework.decorators import action # 126
from rest_framework.response import Response # 126
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Recipe,
    Tag, # 92
    Ingredient, # 107
)
from recipe import serializers


# ModelViewsetはとりわけModelとの連動を強化した親クラス。
@extend_schema_view( # 131 Implement recipe filter featureで追加
    list=extend_schema( # ここでlistエンドポイントであることを指定
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR, # String
                description='Comma separated list of tag IDs to filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter',
            )
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    # serializer_class = serializers.RecipeSerializer
    serializer_class = serializers.RecipeDetailSerializer # Detailの方がCRUD全てを使うので、RecipeSerializerではなくこちらをデフォルトにする
    queryset = Recipe.objects.all() # querysetはこのViewSetの中で触れるObjectのリスト
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # 131 Implement recipe filter feature
    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        # パラメーターについている"1,2,3"などの文字列を[1,2,3]のInt配列にする。
        return [int(str_id) for str_id in qs.split(',')]

    # Overrideする。list取得専用...ではない！
    # これは実はdetailの時も呼び出されるが、その場合はget_querysetが呼び出された後に、DRFの内部でpk=pkのオブジェクトが呼び出されている。分かりづらい。。。
    # Claude先生様様。https://claude.ai/chat/3924e0c9-6f5a-42b5-8700-10dd9eb32643
    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        # return self.queryset.filter(user=self.request.user).order_by('-id') # ちゃんと手でロジックをかませている。。

        # 131 Implement recipe filter feature
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

    # detail取得用
    def get_serializer_class(self):
        """Return teh sereializer class for request."""
        if self.action == 'list': # これはurlを見て、recipes/などでアクセスすると、勝手にaction属性にlistをつけてくれるらしい。。
            return serializers.RecipeSerializer
        elif self.action == 'upload_image': # 126 Implement image API
            return serializers.RecipeImageSerializer # 下にあるupload_image関数から呼び出すために。

        return self.serializer_class

    # 85: implement create api
    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user) # ユーザはこちらで追加することにより、ユーザ側でのPOST時にユーザIDを含める必要がなくなる。

    # 126 Implement image API
    @action(methods=['POST'], detail=True, url_path='upload-image') # POST, detail（リストではなく）URLへのアクセス、url_pathがupload-imageの時に呼び出すよ、という意味のデコレータ。
    def upload_image(self, request, pk=None):
        """Upload an image to recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 117 Refactor recipe views
@extend_schema_view( # 133 Implement tag and ingredient filtering
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_by',
                OpenApiTypes.INT, enum=[0,1],
                description='Filter by items assigned to recipes.'
            )
        ]
    )
)
class BaseRecipeAttrViewSet(mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """Base viewset for recipe attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        # return self.queryset.filter(user=self.request.user).order_by('-name')

        # 133 Implement tag and ingredient filtering
        assigned_only = bool( # intにしてからboolに変換
            int(self.request.query_params.get('assigned_only', 0)) # 0はアサインされていなければ代入される値
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()


# AFTER REFACTORING: 92 Implement tag listing API
class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()

# AFTER REFACTORING: 107 Implement ingredient listing API
class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()


# # 92 Implement tag listing API
# class TagViewSet(mixins.DestroyModelMixin, # 96はこの1行だけ追加
#                  mixins.UpdateModelMixin, # 94はこの1行だけ追加
#                  mixins.ListModelMixin,
#                  viewsets.GenericViewSet):
#     """Manage tags in the database."""
#     serializer_class = serializers.TagSerializer
#     queryset = Tag.objects.all()
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         """Filter queryset to authenticated user."""
#         return self.queryset.filter(user=self.request.user).order_by('-name')


# # 107 Implement ingredient listing API
# class IngredientViewSet(mixins.DestroyModelMixin, # 111 Implement delete ingredient API
#                         mixins.UpdateModelMixin, # 109 Implement update ingredient API
#                         mixins.ListModelMixin, # 107
#                         viewsets.GenericViewSet): # 107
#     """Manage ingredients in the database."""
#     serializer_class = serializers.IngredientSerializer
#     queryset = Ingredient.objects.all()
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         """Filter queryset to authenticated user."""
#         return self.queryset.filter(user=self.request.user).order_by('-name')



