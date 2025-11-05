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

## LangGraph 対応について

本アプリには、従来の `/ask` エンドポイント(直接OpenAI互換API呼び出し)に加えて、LangGraph を利用した `/ask_graph` エンドポイントを追加しています。初期は単一ノードでしたが、現在は「天気ツール」ノードを含む条件分岐付きのグラフへ拡張しています。ツール呼び出し・分岐・要約などを段階的に追加しやすい構造です。

### 呼び出し比較

| 用途 | エンドポイント | 特徴 |
|------|----------------|------|
| 従来処理 | `/ask` | 直接呼び出し + (天気自動検出機能あり) |
| LangGraph | `/ask_graph` | 条件分岐 / 天気ツール / 将来拡張用 |

### リクエスト例 (JavaScript / Fetch)

```javascript
const form = new FormData();
form.append('question', 'LangGraphで何ができますか?');
form.append('assistant', 'You are a helpful assistant.');

fetch('/ask_graph', { method: 'POST', body: form, credentials: 'include' })
    .then(r => r.json())
    .then(console.log);
```

### cURL 例

```bash
curl -X POST -F "question=LangGraphの概要を教えて" -F "assistant=You are a helpful assistant." \
    -b cookie.txt -c cookie.txt \
    http://localhost/ask_graph
```

### 実装概要

`app/graph.py` に以下を定義:
- ChatState (messages / needs_weather / weather_payload など)
- build_graph(): classify -> (weather?) -> model の条件付きフロー
- classify ノード: 天気関連キーワード判定
- weather ノード: Open-Meteo API から現在気象を取得し system メッセージに追加

`app/app.py`:
- OpenAIクライアント初期化後に `graph = build_graph(client)`
- `/ask_graph` ルート: Redis履歴を state に渡し `graph.invoke()` で応答生成

### 環境変数

`.env` で以下を設定可能です:
```
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1   # 公式エンドポイントの場合 (ローカル/互換エンドポイント利用時は置き換え)
SECRET_KEY=your_flask_secret
```

### 拡張のヒント

1. 複数ツール: Web検索 / 計算 / ドキュメント検索ノードを追加
2. 高度分類: embeddings + 意図分類 / LLM でルーティング精度向上
3. 要約ノード: 長会話の圧縮 (periodic summarization) でトークン削減
4. ストリーミング: SSE / WebSocket で逐次表示 (LangGraph streaming)
5. チェックポイント: LangGraph の checkpoint 機能で state を永続化し巻き戻し / 再試行

### 天気ツールについて

判定対象キーワード: `天気`, `気温`, `weather`, `forecast`

対応都市 (単純マッピング): 東京 / 大阪 / 札幌 / 名古屋 / 福岡 (英語表記も可)。
質問文にこれら都市名が含まれていれば該当座標を利用、なければデフォルト=東京。`/ask` 側にも同じロジックを統合済みです (環境変数 `WEATHER_TOOL_ENABLED=false` で無効化可能)。

利用 API: [Open-Meteo](https://open-meteo.com/) （APIキー不要 / 無料）。

挿入される system メッセージ例:
```
[Weather Data] 東京: 気温 25.1°C 湿度 40% 風速 3.2m/s (観測時刻 2025-11-05 02:00 UTC). この情報は Open-Meteo API から取得した速報値です。AI 応答と併せて参考にしてください。
```

エラー時は: `[Weather Data] 取得失敗: ...` を system メッセージとして渡し、モデル応答は通常続行します。

### 使い方例 (天気)
```
質問: 今日の東京の天気と気温を教えて。その後、服装アドバイスもください。
```
→ classify が天気要求を検知 → weather ノードで最新データ挿入 → model が文脈(ユーザ質問 + 天気データ)で回答。

### 注意

- 既存 `/ask` と `/ask_graph` は履歴キーを共通利用するため、混在利用しても履歴は引き継がれます。
- LangGraph の高度機能 (並列/チェックポイント) を使いたい場合は、`graph.py` にノード・条件を追加しコンパイルし直してください。
- 本天気機能は簡易実装のため、地名解釈や気象要素拡張を行う際は NER / 位置API などの導入を検討してください。
