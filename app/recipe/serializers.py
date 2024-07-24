"""
Serializers for recipe APIs
"""
from rest_framework import serializers

from core.models import (
    Recipe,
    Tag, # 92
    Ingredient, # 107
)


# 107 Implement ingredient listing API
class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


# 92 Implement tag listing API
# 99 Nestのために先頭に移動
class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    # 99 Implement create tag feature
    tags = TagSerializer(many=True, required=False) # many=Trueは配列であること。

    # 113 Implement create ingredients feature
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'time_minutes', 'price', 'link',
            'tags', # 99で追加
            'ingredients', # 113で追加
        ]
        read_only_fields = ['id']

    # 101 Implement update recipe tags feature
    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    # 113 Implement create ingredients feature
    # internal onlyのため_をprefixにつける
    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed."""
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            recipe.ingredients.add(ingredient_obj)

    # 99 Implement create tag feature
    def create(self, validated_data):
        """Create a recipe."""
        tags = validated_data.pop('tags', []) # ここをPOPにしないと、その後のcreateの過程で以下のエラーが出る。many to many fieldへのダイレクトなアサインメントは禁止されているらしい。
        # TypeError: Direct assignment to the forward side of a many-to-many set is prohibited. Use tags.set() instead.

        ingredients = validated_data.pop('ingredients', []) # 113で追加

        recipe = Recipe.objects.create(**validated_data) # recipeオブジェクトを作る

        # auth_user = self.context['request'].user # serializerの中から認証ユーザのオブジェクトを取得する
        # for tag in tags:
        #     tag_obj, created = Tag.objects.get_or_create( # 既存のタグがあれ取得する、なければ新規作成
        #         user=auth_user,
        #         **tag,
        #     )
        #     recipe.tags.add(tag_obj)
        # 上のauth以下をリファクタリング
        self._get_or_create_tags(tags, recipe)

        self._get_or_create_ingredients(ingredients, recipe) # 113で追加

        return recipe # ここでreturnするrecipeが、viewsetの中のperform_createへシリアライズ済みデータとして渡される。

    # 101 Implement update recipe tags feature
    def update(self, instance, validated_data):
        """Update recipe."""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None) # 115で追加
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance) # これで配列ごと抜き出すのか。。Serializerのインナーメソッドらしい。あ、違った。これから書くんだ。

        # 115で追加
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value) # こんな書き方あるんだ。。

        instance.save() # これなんぞ？
        return instance


class RecipeDetailSerializer(RecipeSerializer): # RecipeSerializerを継承する！！！
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description', 'image'] # 詳細ビューではdescriptionを追加する！！！ imageは#127で追加。


# 126 Implement image API
# 大前提として、レシピの登録APIと、画像のアップロードAPIはわける。これはRESTのプラクティス（？）で
# 1つのAPIの中にJSONや画像など、複数のデータ型を混在させるのは避けた方が良い、というのがある。
# そのほうがデータ構造を簡単に保てるし、開発しやすいし、可読性も高い。
class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes."""

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}
