"""
URL mappings for the recipe app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from recipe import views


router = DefaultRouter()
router.register('recipes', views.RecipeViewSet)
# 上の1行だけで、以下のエンドポイントが自動生成されて、自分でurlpatternsに指定する必要がなくなる。
# 詳しくはNotion。https://www.notion.so/13-Build-recipe-API-9d7bb37cc5c347bfb4d59651141f88f8

# 92 Implement tag listing API
router.register('tags', views.TagViewSet)

# 107 Implement ingredient listing API
router.register('ingredients', views.IngredientViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]
