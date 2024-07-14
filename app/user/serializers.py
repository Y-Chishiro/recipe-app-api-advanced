"""
Serializers for the user API View.
"""
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta: # DRFに対して扱いたいモデルやフィールドを教える
        model = get_user_model()
        fields = ['email', 'password', 'name'] # レスポンスに必要なフィールド
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}} # それぞれのフィールドにメタデータを与えたいときのkwargs

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data): # updateメソッドをオーバーライド。instanceは今のユーザーのinstance。
        """Update and return user."""
        print("here?")
        # print("validated data: ", validated_data)
        password = validated_data.pop('password', None) # passwordを取得してから削除する。passwordだけは変更の手順が違うため。
        user = super().update(instance, validated_data) # superはModelSerializerの親関数。これでupdateをするのがお約束。

        # もしパスワードも変更要望があれば
        if password:
            user.set_password(password)
            user.save()

        return user # 最後にuserを返すのがupdateをオーバーライドした時のお約束


# 特定のモデルに紐づかないシリアライザを作る。
class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    # Validateはビューにデータを持ったPOSTリクエストが来た時に呼ばれるメソッド。validation stageがある。
    # データの内容をvalidateする。returnを見ればわかるが、アトリビュートを受け取って、中身を精査、更新、必要に応じて要素を追加し、更新したアトリビュートを返す
    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get('email') # リクエストのデータ（attributes）からemailをretrieveする。
        password = attrs.get('password') # 同じくpassword

        # authenticateはdjangoのメソッド。
        # request, username, passwordの3つを渡すと、DBに実際にユーザが存在して、パスワードもあっていれば、userオブジェクトを返す
        # なんらかエラーがあれば空のオブジェクトを返す
        user = authenticate(
            request=self.context.get('request'), # contextの指定だが、これをなぜやるかは先生も知らないとのこと。必須だから書いている。
            username=email, # 我々の仕組みではユーザネーム=emailなので、emailを渡す
            password=password,
        )
        if not user:
            msg = ('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization') # メッセージを含むHTTP_400_REQUESTを返す

        attrs['user'] = user # 認証がうまく行ったら、アトリビュートの中にもうユーザーを含めちゃう。
        return attrs # 最終的に上書きしたアトリビュートを返す
