from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import tempfile
import base64

# ===============================
# Flask App
# ===============================
app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

# ===============================
# Roboflow Config
# ===============================
ROBOFLOW_API_KEY = os.environ.get("ROBOFLOW_API_KEY")
WORKFLOW_URL = "https://serverless.roboflow.com/max-abkdo/workflows/detect-count-and-visualize-7"

# ===============================
# Serve Frontend
# ===============================
@app.route("/")
def index():
    return send_from_directory("../frontend", "peoplecounterai_web.html")

# ===============================
# Count People API
# ===============================
@app.route("/count-people", methods=["POST"])
def count_people():
    if "image" not in request.files:
        return jsonify({"error": "no_image"}), 400

    image_file = request.files["image"]

    # save temp image
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        image_file.save(tmp.name)
        image_path = tmp.name

    try:
        with open(image_path, "rb") as f:
            response = requests.post(
                WORKFLOW_URL,
                headers={"Content-Type": "application/json"},
                json={
                    "api_key": ROBOFLOW_API_KEY,
                    "inputs": {
                        "image": {
                            "type": "base64",
                            "value": base64.b64encode(f.read()).decode("utf-8")
                        }
                    }
                },
                timeout=60
            )

        result = response.json()
        print("ROBOFLOW RESULT =", result)

        outputs = result.get("outputs", [])
        output = outputs[0] if outputs else {}

        people_count = output.get("count_objects", 0)

        image_obj = output.get("output_image")
        image_data = None
        if image_obj and image_obj.get("type") == "base64":
            image_data = "data:image/jpeg;base64," + image_obj.get("value")

        return jsonify({
            "people_count": int(people_count),
            "image_data": image_data
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "ai_failed"}), 500

    finally:
        if os.path.exists(image_path):
            os.remove(image_path)

# ===============================
# Run App
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
