from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests, os, base64

app = Flask(__name__, static_folder="../frontend", static_url_path="/")
CORS(app)

# =========================
# Roboflow config
# =========================
ROBOFLOW_API_KEY = os.environ.get("ROBOFLOW_API_KEY")
WORKFLOW_URL = "https://serverless.roboflow.com/max-abkdo/workflows/detect-count-and-visualize-7"

# =========================
# Serve frontend
# =========================
@app.route("/")
def serve_frontend():
    return send_from_directory("../frontend", "peoplecounterai_web.html")

# =========================
# AI inference endpoint
# =========================
@app.route("/count-people", methods=["POST"])
def count_people():
    if "image" not in request.files:
        return jsonify({"error": "no_image_uploaded"}), 400

    image_file = request.files["image"]

    # 🔹 แปลงรูปเป็น base64
    image_bytes = image_file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    try:
        response = requests.post(
            WORKFLOW_URL,
            headers={"Content-Type": "application/json"},
            json={
                "api_key": ROBOFLOW_API_KEY,
                "inputs": {
                    "image": {
                        "type": "base64",
                        "value": image_base64
                    }
                }
            },
            timeout=60
        )

        result = response.json()
        print("ROBOFLOW RESULT =", result)

        # workflow จะ return list เสมอ
        item = result[0]

        # นับจำนวนคน
        count_objects = item.get("count_objects", {})
        people_count = count_objects.get("person", 0)

        # ภาพผลลัพธ์
        image_data = item.get("output_image")
        if image_data and not image_data.startswith("data:"):
            image_data = "data:image/jpeg;base64," + image_data

        return jsonify({
            "people_count": int(people_count),
            "image_data": image_data
        })

    except Exception as e:
        print("ERROR CALLING ROBOFLOW:", e)
        return jsonify({"error": "ai_failed"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
