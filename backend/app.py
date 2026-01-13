from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import base64

app = Flask(__name__, static_folder="../frontend", static_url_path="/")
CORS(app)

# =========================
# Roboflow CONFIG
# =========================
ROBOFLOW_API_KEY = "wKpIUIIREpwp9a613Cii"   # 🔴 แนะนำย้ายไปเป็น ENV ในอนาคต
WORKSPACE = "max-abkdo"
WORKFLOW_ID = "detect-count-and-visualize-4"

ROBOFLOW_URL = f"https://serverless.roboflow.com/{WORKSPACE}/{WORKFLOW_ID}"

# =========================
# Serve Frontend
# =========================
@app.route("/")
def serve_frontend():
    return send_from_directory("../frontend", "peoplecounterai_web.html")

# =========================
# AI Count People Endpoint
# =========================
@app.route("/count-people", methods=["POST"])
def count_people():
    if "image" not in request.files:
        return jsonify({"error": "no_image_uploaded"}), 400

    image_file = request.files["image"]

    try:
        # ส่งรูปไป Roboflow
        response = requests.post(
            ROBOFLOW_URL,
            params={"api_key": ROBOFLOW_API_KEY},
            files={"image": image_file},
            timeout=60
        )

        if response.status_code != 200:
            return jsonify({"error": "roboflow_failed"}), 500

        data = response.json()

        # 🔹 ดึงจำนวนคน (แล้วแต่ workflow)
        people_count = (
            data.get("count")
            or data.get("people_count")
            or 0
        )

        # 🔹 ดึงรูปผลลัพธ์ (base64)
        image_base64 = data.get("image")

        if image_base64:
            image_base64 = "data:image/jpeg;base64," + image_base64

        return jsonify({
            "people_count": int(people_count),
            "image_data": image_base64
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "processing_failed"}), 500


# =========================
# Run App
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
