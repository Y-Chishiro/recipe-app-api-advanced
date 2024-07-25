FROM python:3.12.4-alpine3.20
# alpineは最も軽量なpythonイメージ

LABEL maintainer="yusuke"
# 誰がメンテナンスするか？

ENV PYTHONUNBUFFERED 1
# デバッグ時の出力をそのまま取得する（？）

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./scripts /scripts
COPY ./app /app
WORKDIR /app
EXPOSE 8000
# 実行に必要なファイル、フォルダの移動

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev linux-headers && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol && \
    chmod -R +x /scripts

# &&が命令の切れ目
# venv 実行環境を作る
# pipのアップグレード
# requirementsのインストール
# tempファイルの削除
# アルパインイメージの中に新しいユーザの作成。ルートユーザを使わないために。django-userはユーザの名前。なんでも良いが、わかりやすさ優先。

# chown = Change owner
# chmod = Change mode

ENV PATH="/scripts:/py/bin:$PATH"
# アルパインイメージの中で、環境変数のアップデート

USER django-user

CMD ["run.sh"]
