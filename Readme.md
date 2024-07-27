# chatgpt_webapp

chatgptに質問をしてみて回答を得るwebアプリになります。

## 事前作業

あらかじめdocker-composeインストールを実施していること。

本プログラムはmac/Linuxで動かしてください。

ChatGPT APIもあらかじめ入手してください。

## 初期設定

```bash
git clone https://github.com/naritomo08/chatgpt_webapp.git
cd chatgpt_webapp.git
rm -rf .git
cp app
cp variable_ref.py variable.py
vi variable.py

以下の””の中にAPIキーを入力する。

api_key = ""

cd ..

docker-compose up -d
```

## サイト参照

```bash
http://localhost:3100/
```

## 質問実施履歴

```bash
以下のファイルに保管されています。

app/output/chatgpt_log.log
```

## Webアプリ起動

```bash
docker-compose down
```

## Webアプリ停止

```bash
docker-compose down
```
