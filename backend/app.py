from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder="../frontend", static_url_path="/")
CORS(app)

# -------------------------
# เสิร์ฟหน้าเว็บ
# -------------------------
@app.route("/")
def serve_frontend():
    return send_from_directory("../frontend", "peoplecounterai_web.html")


# -------------------------
# endpoint หลอกไว้ก่อน (ยังไม่ใช้ AI)
# -------------------------
@app.route("/count-people", methods=["POST"])
def count_people():
    return jsonify({
        "message": "AI inference is temporarily disabled on this server",
        "people_count": 0
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
