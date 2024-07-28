from flask import Flask, request, render_template, jsonify, redirect, url_for, flash
import openai
import logging
from datetime import datetime
import os
from logging.handlers import TimedRotatingFileHandler
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from user import User, get_user, users

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  # セッションのためのシークレットキーを設定

# CSRF保護の設定
csrf = CSRFProtect(app)

# 環境変数からOpenAIのAPIキーを設定
openai.api_key = os.getenv('OPENAI_API_KEY')

# Flask-Loginの設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return next((user for user in users.values() if user.id == int(user_id)), None)

# ロギングの設定
log_dir = 'output'
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, 'chatgpt_log.log')

# TimedRotatingFileHandlerを使ったロギング設定
handler = TimedRotatingFileHandler(log_file_path, when='midnight', interval=1, backupCount=7)
handler.suffix = "%Y-%m-%d"
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

def ask_chatgpt(question):
    try:
        # ChatGPTに質問を送り、回答を得る
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question}
            ]
        )

        # 回答を取得
        answer = response.choices[0].message['content']
        return answer

    except Exception as e:
        return f"An error occurred: {e}"

def format_question(question):
    formatted = question.replace("\n", "<br>")
    return formatted

def format_answer(answer):
    formatted = answer.replace("```python", "<pre><code class='language-python'>").replace("```", "</code></pre>")
    formatted = formatted.replace("\n", "<br>")
    formatted = formatted.replace("<br><pre>", "<pre>").replace("</pre><br>", "</pre>")
    return formatted

def log_interaction(user, question, answer):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp}\nUser: {user.username}\nQuestion:\n{question}\nAnswer:\n{answer}\n{'-'*80}"
    logging.info(log_entry)

@app.route("/", methods=["GET"])
@login_required
def index():
    return render_template("index.html", username=current_user.username)

@app.route("/ask", methods=["POST"])
@login_required
def ask():
    question = request.form["question"]
    raw_answer = ask_chatgpt(question)
    formatted_question = format_question(question)
    formatted_answer = format_answer(raw_answer)
    log_interaction(current_user, question, raw_answer)
    return jsonify(question=formatted_question, answer=formatted_answer)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = get_user(username)
        if user and user.password == password:
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))  # ログイン失敗時にリダイレクトする
    return render_template("login.html")

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify(status="OK", timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == '__main__':
    # Flaskアプリを実行
    app.run(host='0.0.0.0', port=3100, debug=False)