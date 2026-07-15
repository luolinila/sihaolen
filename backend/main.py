"""
sihaolen 冷笑话后端服务
唯一接口：GET /api/joke/random — 随机返回一条冷笑话
"""

from flask import Flask, jsonify, send_from_directory
import pymysql
import os

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False  # 返回中文不转义

# 数据库配置
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "cafgbifi0b"),
    "database": os.getenv("DB_NAME", "sihaolen"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


def get_connection():
    return pymysql.connect(**DB_CONFIG)


@app.route("/api/joke/random")
def random_joke():
    """随机返回一条冷笑话"""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, content, category, length, difficulty "
                "FROM jokes ORDER BY RAND() LIMIT 1"
            )
            row = cursor.fetchone()
            if row is None:
                return jsonify({"error": "暂无冷笑话数据"}), 404
            return jsonify(row)
    except pymysql.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/download")
def download():
    """下载 嘶好冷.exe"""
    return send_from_directory(
        os.path.dirname(os.path.abspath(__file__)),
        "嘶好冷.exe",
        as_attachment=True,
        download_name="嘶好冷.exe",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
