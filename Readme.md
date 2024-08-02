# chatgpt_webapp

chatgptに質問をしてみて回答を得るwebアプリになります。

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

api_key = ""

docker-compose up -d
```

## サイト参照

```bash
http://localhost:3100/
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
