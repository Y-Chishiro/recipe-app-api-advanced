"""
Tests for models
"""
from unittest.mock import patch
from decimal import Decimal # Recipeオブジェクトのフィールドの1つに使用

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


# 90 Tagクラスのテスト用
def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'], # 1つ目をインプットすると2つ目に自動変換されていることを期待するテスト
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_suepruser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    """Recipe model"""
    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe description.',
        )

        self.assertEqual(str(recipe), recipe.title)

    # 90 Add tag model
    def test_create_tag(self):
        """Test creating a tag is successful."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)

    # 105 Add Ingredient model
    def test_create_ingredient(self):
        """Test creating an ingredient is successful."""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name='ingredient1'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    # 124 Modify recipe model
    @patch('core.models.uuid.uuid4') # 指定したパスの関数（uuid.uuid4）を一時的にモック板に入れ替える
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        # このテストの意味：
        # テストしたい関数はmodels.pyに定義したrecipe_file_name_uuid関数が期待通りの動きをするかどうか。
        # この関数はユーザがアップロードした画像ファイルの名前を渡すと、拡張子はそのままで、名前部分をuuid.uuid4関数が返す
        # ユニークな文字列に変更して返す。これによっておそらくファイル名が揃って良いのか？
        # テストする時はuuidが毎回違う結果を返すと困るので、recipe_file_name_uuid内でuuid.uuid4関数が呼ばれた時の
        # 結果をモックから返す（固定値にする）ために、@patchを使っている。

        uuid = 'test-uuid'
        mock_uuid.return_value = uuid # これがmockオブジェクト。return_value属性をつけると自動的に@Patchで指定した関数のmockオブジェクトになるらしい。むずすぎる。
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
