"""
Database models.
"""
import uuid # 124
import os # 124

from django.conf import settings

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


# 124 Modify recipe model
# アップロードされた画像を拡張子だけ残して、ファイル名をuuid4で出力された16ビットのランダムな文字列にする。
def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image."""
    ext = os.path.splitext(filename)[1] # 拡張子を取り出して
    filename = f'{uuid.uuid4()}{ext}' # uuid.uuid4でランダムに生成されたユニークな識別子（文字列）を取り出してファイル名にする。例：f1e6b391-3b9c-4a4c-8b9f-8c8f5db692d5

    return os.path.join('uploads', 'recipe', filename)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save, and return a new user."""
        if not email:
            raise ValueError('User must have an email adrress.')
        user = self.model(email=self.normalize_email(email), **extra_fields) # UserManagerはUserに紐づけられている
        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True # これはUserモデルデフォルトのフィールド
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    # abstratbaseuserは認証機能などを管理、permissionmixinはフィールドごとのパーミッションなど
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name =models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Recipe(models.Model):
    """Recipe object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, # 外部キーとしてユーザモデルを指定。Userモデルの編集や変更があることがあるので、settingsのAUTH_USER_MODELを呼び出すのがベストプラクティス。
        on_delete=models.CASCADE, # ユーザが削除された時、紐づいたレシピも全て削除する
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)

    image = models.ImageField(null=True, upload_to=recipe_image_file_path) # 124 Modify recipe model

    # 90 Add tag model
    tags = models.ManyToManyField('Tag')

    # 105 で追加
    ingredients = models.ManyToManyField('Ingredient')

    def __str__(self):
        return self.title


# 90 Add tag model
class Tag(models.Model):
    """Tag for filtering recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


#105 Add Ingredient model
class Ingredient(models.Model):
    """Ingredient for recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
