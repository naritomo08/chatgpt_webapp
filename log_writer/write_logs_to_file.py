import redis
import json
import time
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, timedelta
import threading
import atexit

# Redisクライアントの設定
redis_client = redis.Redis(host='redis', port=6379, db=0)

# ログディレクトリとファイルの設定
log_dir = './output/log'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, 'chatgpt_log.log')

# 古いログを削除する関数
def cleanup_old_logs(log_dir, days_to_keep=7):
    """指定された日数より古い chatgpt_log.log.yyyymmdd 形式のログファイルを削除"""
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    for file_name in os.listdir(log_dir):
        if file_name.startswith("chatgpt_log.log."):
            # ファイル名から日付部分を抽出
            date_part = file_name.replace("chatgpt_log.log.", "")
            try:
                file_date = datetime.strptime(date_part, "%Y%m%d")
                if file_date < cutoff_date:
                    os.remove(os.path.join(log_dir, file_name))
                    print(f"Deleted old log file: {file_name}")
            except ValueError:
                print(f"Skipped invalid log file: {file_name}")  # 日付部分が不正な場合はスキップ

# 定期的にログ削除を実行する関数
def schedule_cleanup(interval, log_dir, days_to_keep):
    """一定間隔で古いログファイルを削除"""
    while True:
        try:
            cleanup_old_logs(log_dir, days_to_keep)
        except Exception as e:
            print(f"Error during log cleanup: {e}")
        time.sleep(interval)

# ロガーの設定
def setup_logger(log_file):
    """ログローテーション用ロガーを設定"""
    handler = TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",
        interval=1,
        backupCount=0  # 自動削除は行わず、手動で管理
    )
    handler.suffix = "%Y%m%d"  # ローテーション後のファイル名形式

    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger('task_logger')
    logger.setLevel(logging.INFO)

    # ハンドラーを追加
    if not logger.hasHandlers():
        logger.addHandler(handler)

    # プログラム終了時にクリーンアップ
    @atexit.register
    def cleanup():
        for h in logger.handlers:
            h.close()
            logger.removeHandler(h)

    return logger

# ロガーの初期化
logger = setup_logger(log_file)

# Redisからログを取得してファイルに書き込む関数
def process_redis_logs(logger):
    """Redisからログを取得してファイルに書き込む"""
    while True:
        try:
            log_entry = redis_client.lpop('chatgpt_logs')
            if log_entry:
                log_entry = json.loads(log_entry)
                log_message = f"{log_entry['timestamp']}\nUser: {log_entry['user']}\nQuestion:\n{log_entry['question']}\nAnswer:\n{log_entry['answer']}\n{'-'*80}"
                logger.info(log_message)
            else:
                time.sleep(10)  # Redisが空の場合、10秒待機
        except Exception as e:
            logger.error(f"Error while processing logs: {e}")
            time.sleep(10)  # エラー発生時も10秒待機して再試行

# メイン処理
if __name__ == "__main__":
    # 定期的なログ削除スレッドを開始
    cleanup_thread = threading.Thread(
        target=schedule_cleanup,
        args=(3600, log_dir, 7),  # 1時間ごとにログ削除を実行
        daemon=True
    )
    cleanup_thread.start()

    # Redisログ処理の開始
    process_redis_logs(logger)
