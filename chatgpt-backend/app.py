from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import logging
from datetime import datetime
import os
from logging.handlers import TimedRotatingFileHandler
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from user import User, get_user, users
import json

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# CORSの設定
CORS(app, supports_credentials=True)
#CORS(app, supports_credentials=True, resources={
#    r"/*": {
#        "origins": ["http://your-frontend-domain.com"]  # フロントエンドのURLに置き換える
#    }
#})

# OpenAI APIキーの環境変数設定
openai.api_key = os.getenv('OPENAI_API_KEY')

# ロギングの設定
log_dir = 'output'
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, 'chatgpt_log.log')

handler = TimedRotatingFileHandler(log_file_path, when='midnight', interval=1, backupCount=7)
handler.suffix = "%Y%m%d"
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

# Flask-Loginの設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return next((user for user in users.values() if user.id == int(user_id)), None)

def ask_chatgpt(question):
    try:
        # ChatGPTに質問を送り、回答を得る
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question}
            ]
        )

        # 回答を取得
        answer = response.choices[0].message.content
        if not answer:
            return "No response from API"
        return answer

    except Exception as e:
        logging.error(f"Error contacting OpenAI API: {e}")
        return f"An error occurred: {e}"

def log_interaction(user, question, answer):
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {
            "timestamp": timestamp,
            "user": user.username,
            "question": question,
            "answer": answer
        }
        logging.info(json.dumps(log_entry, ensure_ascii=False, indent=2))
    except Exception as e:
        logging.error(f"Logging error: {e}")

def format_question(question):
    """質問をHTML形式にフォーマットします。"""
    formatted = question.replace("\n", "<br>")
    return formatted

def format_answer(answer):
    """回答をHTML形式にフォーマットします。"""
    formatted = answer.replace("```python", "<pre><code class='language-python'>").replace("```", "</code></pre>")
    formatted = formatted.replace("\n", "<br>")
    formatted = formatted.replace("<br><pre>", "<pre>").replace("</pre><br>", "</pre>")
    return formatted

@app.route("/ask", methods=["POST"])
@login_required
def ask():
    question = request.json.get("question")  # JSONデータから質問を取得
    if not question:
        return jsonify({"error": "Question is required"}), 400

    raw_answer = ask_chatgpt(question)
    formatted_question = format_question(question)
    formatted_answer = format_answer(raw_answer)
    log_interaction(current_user, question, raw_answer)
    return jsonify(question=formatted_question, answer=formatted_answer)

@app.route("/login", methods=["GET", "POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return jsonify(success=True), 200
    
    if request.method == "POST":
        username = request.json["username"]
        password = request.json["password"]
        user = get_user(username)
        if user and user.password == password:
            login_user(user)
            return jsonify({"success": True, "message": "Logged in successfully."})
        else:
            return jsonify({"success": False, "message": "Invalid username or password."})
    
    # GETメソッドの対応（リダイレクトまたは簡単なメッセージを返す）
    return jsonify({"success": False, "message": "Use POST method for login."})

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify(success=True)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify(status="OK", timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# 設定を提供するエンドポイントを追加
@app.route("/config", methods=["GET"])
def get_config():
    config = {
        "apiBaseUrl": os.getenv('REACT_APP_API_BASE_URL'),
        "timeZone": os.getenv('TZ', 'Asia/Tokyo')
    }
    return jsonify(config)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3100, debug=False)