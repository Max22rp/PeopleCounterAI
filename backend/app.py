from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests, os, tempfile, base64

app = Flask(__name__, static_folder="../frontend", static_url_path="/")
CORS(app)

ROBOFLOW_API_KEY = os.environ.get("ROBOFLOW_API_KEY")  # แนะนำให้ตั้งใน Render
WORKFLOW_URL = "https://serverless.roboflow.com/max-abkdo/workflows/detect-count-and-visualize-7"

@app.route("/")
def serve_frontend():
    return send_from_directory("../frontend", "peoplecounterai_web.html")


@app.route("/count-people", methods=["POST"])
def count_people():
    if "image" not in request.files:
        return jsonify({"error": "no_image"}), 400

    image_file = request.files["image"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        image_file.save(tmp.name)
        image_path = tmp.name

    try:
        with open(image_path, "rb") as f:
            response = requests.post(
                WORKFLOW_URL,
                params={"api_key": ROBOFLOW_API_KEY},
                files={"image": f},
            )

        result = response.json()
        print("ROBOFLOW RESULT =", result)

        item = result[0] if isinstance(result, list) else result

        people_count = (
            item.get("count_objects")
            or item.get("people_count")
            or 0
        )

        image_data = item.get("output_image")

        if image_data and not image_data.startswith("data:"):
            image_data = "data:image/jpeg;base64," + image_data

        return jsonify({
            "people_count": int(people_count),
            "image_data": image_data
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "ai_failed"}), 500

    finally:
        os.remove(image_path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
