from flask import Flask, request, render_template, jsonify
import openai
import logging
from datetime import datetime
import os
import variable as v

app = Flask(__name__)

# OpenAIのAPIキーを設定
openai.api_key = v.api_key

# ロギングの設定
log_dir = 'output'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(filename=os.path.join(log_dir, 'chatgpt_log.log'), level=logging.INFO, format='%(message)s')

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

def log_interaction(question, answer):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp}\nQuestion:\n{question}\nAnswer:\n{answer}\n{'-'*80}"
    logging.info(log_entry)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    question = request.form["question"]
    raw_answer = ask_chatgpt(question)
    formatted_question = format_question(question)
    formatted_answer = format_answer(raw_answer)
    log_interaction(question, raw_answer)
    return jsonify(question=formatted_question, answer=formatted_answer)

if __name__ == '__main__':
    # Flaskアプリを実行
    app.run(host='0.0.0.0', port=3100, debug=False)
