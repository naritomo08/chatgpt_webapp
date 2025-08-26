from flask import Flask, request, render_template, jsonify, session, redirect, url_for, flash
import openai
import logging
from datetime import datetime
import os
import redis
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from user import get_user, users
import json
from forms import LoginForm

# 追加: Markdownレンダリング用
import markdown as md
import bleach

# 追加: レイテンシ計測
import time

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_fixed_secret_key_here')  # セッションのためのシークレットキーを設定

# CSRF保護の設定
csrf = CSRFProtect(app)

# 環境変数からOpenAIのAPIキーを設定
openai.api_key = os.getenv('OPENAI_API_KEY')

# Redisクライアントの設定
redis_client = redis.Redis(host='redis', port=6379, db=0)

# Redis接続の確認
try:
    redis_client.ping()
except redis.ConnectionError:
    raise RuntimeError("Redis server is not available")

# Flask-Loginの設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return next((user for user in users.values() if user.id == int(user_id)), None)

def get_chat_history(user_id):
    # Redisからユーザーのチャット履歴を取得
    history = redis_client.get(f"chat_history:{user_id}")
    if history:
        return json.loads(history)
    return []

def save_chat_history(user_id, history):
    # Redisにユーザーのチャット履歴を保存
    redis_client.set(f"chat_history:{user_id}", json.dumps(history))

# ===== Markdown -> 安全な HTML 変換（追加） =====
ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS.union({
    'p','pre','code','blockquote','hr','br',
    'h1','h2','h3','h4','h5','h6',
    'ul','ol','li','table','thead','tbody','tr','th','td',
    'strong','em','del','img','a','span'
})
ALLOWED_ATTRS = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    'a': ['href', 'title', 'rel', 'target'],
    'img': ['src', 'alt', 'title'],
    'code': ['class'],
    'span': ['class'],
    'th': ['align'],
    'td': ['align'],
}
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

def render_markdown(text: str) -> str:
    """Markdown を HTML に変換し、許可タグのみ残す"""
    if not text:
        return ""
    html = md.markdown(
        text,
        extensions=[
            'fenced_code',      # ```code``` 対応
            'codehilite',       # Pygments でハイライト（CSS 必要）
            'tables',           # テーブル
            'sane_lists',
            'toc',
            'smarty'
        ],
        extension_configs={
            'codehilite': {
                'guess_lang': False,
                'noclasses': False,  # CSS クラスを使う
            }
        }
    )
    cleaned = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        protocols=ALLOWED_PROTOCOLS,
        strip=True
    )
    return bleach.linkify(cleaned)

# Jinja フィルタ登録
app.jinja_env.filters['markdown'] = render_markdown
# ==============================================

def ask_chatgpt(question, user_id):
    try:
        # ユーザーのチャット履歴を取得
        chat_history = get_chat_history(user_id)

        # 現在の質問をチャット履歴に追加
        chat_history.append({"role": "user", "content": question})

        # ChatGPTに質問を送り、回答を得る
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=chat_history
        )

        # 回答を取得
        answer = response.choices[0].message.content

        # 回答をチャット履歴に追加
        chat_history.append({"role": "assistant", "content": answer})

        # 更新されたチャット履歴を保存
        save_chat_history(user_id, chat_history)

        return answer

    except Exception as e:
        logging.error(f"Error communicating with OpenAI: {e}")
        return "An error occurred while communicating with the AI."

# ===== Markdown 対応 =====
def format_question(question):
    return render_markdown(question)

def format_answer(answer):
    return render_markdown(answer)
# ========================

# モデル別メトリクスを何件保持するか（任意）
LATENCY_LIST_MAX = 1000

def log_interaction(user, question, answer, duration_ms=None, duration_s=None):
    """会話ログ（Redis: chatgpt_logs）と、モデル別レイテンシ（Redis: latency:{LLM}）を保存"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = {
        "timestamp": timestamp,
        "user": user.username,
        "question": question,
        "answer": answer,
        "latency_ms": duration_ms,
        "latency_s": duration_s
    }
    redis_client.lpush('chatgpt_logs', json.dumps(log_entry))

    if duration_ms is not None:
        key_ms = f"latency:ms"
        redis_client.lpush(key_ms, duration_ms)
        redis_client.ltrim(key_ms, 0, LATENCY_LIST_MAX - 1)
    if duration_s is not None:
        key_s = f"latency:s"
        redis_client.lpush(key_s, duration_s)
        redis_client.ltrim(key_s, 0, LATENCY_LIST_MAX - 1)

@app.route("/", methods=["GET"])
@login_required
def index():
    chat_history = get_chat_history(current_user.id)  # ユーザーのチャット履歴を取得
    return render_template("index.html", username=current_user.username, chat_history=chat_history)

@app.route("/ask", methods=["POST"])
@login_required
def ask():
    question = request.form["question"]

    # ===== レイテンシ計測開始 =====
    t0 = time.monotonic()

    raw_answer = ask_chatgpt(question, current_user.id)

    t1 = time.monotonic()
    # ===== レイテンシ計測終了 =====

    duration_s = round((t1 - t0), 3)         # 秒（小数第3位まで）
    duration_ms = int(duration_s * 1000)     # ミリ秒（整数）

    # Markdown → HTML（サニタイズ済み）へ
    formatted_question = format_question(question)
    formatted_answer = format_answer(raw_answer)

    # レイテンシ付きでログ保存
    log_interaction(current_user, question, raw_answer, duration_ms, duration_s)

    # 必要ならフロントで表示できるよう同梱
    return jsonify(
        question=formatted_question,
        answer=formatted_answer,
        latency_ms=duration_ms,
        latency_s=duration_s
    )

@app.route("/reset", methods=["POST"])
@login_required
def reset_chat():
    # Redisからユーザーのチャット履歴を削除
    redis_client.delete(f"chat_history:{current_user.id}")
    flash("Chat history has been reset.", "success")
    return redirect(url_for("index"))

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()  # フォームのインスタンスを作成
    if form.validate_on_submit():  # フォームのバリデーションとサブミットの確認
        username = form.username.data
        password = form.password.data
        user = get_user(username)
        if user and user.password == password:
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))
    return render_template("login.html", form=form)  # フォームをテンプレートに渡す

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify(status="OK", timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/error_page', methods=['GET'])
def error_page():
    error_message = session.pop('error_message', "戻るボタンを押してください。")
    return render_template('errors/error.html', error_message=error_message), 500

@app.errorhandler(404)
def show_404_page(error):
    error_message = error.description
    return render_template('errors/error.html', error_message=error_message), 404

@app.errorhandler(400)
def show_400_page(error):
    error_message = error.description
    return render_template('errors/error.html', error_message=error_message), 400

if __name__ == '__main__':
    # Flaskアプリを実行
    app.run(host='0.0.0.0', port=3100, debug=False)