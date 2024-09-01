# chatgpt_webapp

chatgptと会話するwebアプリになります。

## 事前作業

あらかじめdocker-composeインストールを実施していること。

本プログラムはmac/Linuxで動かしてください。

ChatGPT API keyも以下のページからあらかじめ入手してください。

https://platform.openai.com/playground/

## 初期設定

```bash
git clone https://github.com/naritomo08/chatgpt_webapp.git
cd chatgpt_webapp
rm -rf .git
cp .env_ref .env
vi .env

以下の””の中にAPIキーを入力する。

OPENAI_API_KEY = ""

docker-compose up -d
```

## サイト参照

```bash
http://localhost/
→ログイン画面が出るので、testuser/testpasswordを入れてください。
```

## ユーザー設定

```bash
ユーザー追加や変更する際は、user.pyの以下の箇所について書き換えたり、
カンマ追加してユーザー情報を追記してください。

# サンプルユーザーデータ
users = {
    "testuser": User(id=1, username="testuser", password="testpassword")
}

```

## 質問実施履歴

```bash
以下のファイルに保管されています。

log_writer/output/chatgpt_log.log
```

## Webアプリ起動

```bash
docker-compose up -d
```

## Webアプリ停止

```bash
docker-compose down
```

## 注意点

仕組みとしてはChatGPTAPIでは過去のやり取りを覚える機能はないため、あらかじめRedisにやり取りを保存しておき、毎回質問するたびに履歴をつけて会話を送付するようにしています。
注意点はAPIではトークン数で課金され、青天井なので履歴が多くなるとかなり課金されるため、別のネタにする場合は一旦履歴クリアしたほうがいいです。
