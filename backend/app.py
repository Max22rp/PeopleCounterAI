from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from inference_sdk import InferenceHTTPClient
import tempfile, os

app = Flask(__name__, static_folder="../frontend", static_url_path="/")
CORS(app)

# -------------------------
# 1) ตั้งค่าจาก Roboflow
# -------------------------

# api_url มาจากโค้ดตัวอย่างบน Roboflow (หน้า Deploy)
API_URL = "https://serverless.roboflow.com"

# ตรงนี้ให้เอา api_key จากกล่องโค้ด Roboflow มาใส่แทน XXX
# ตัวอย่างในโค้ด Roboflow คือ:
# client = InferenceHTTPClient(api_url="https://serverless.roboflow.com",
#                              api_key="นี่คือคีย์ของคุณ")
API_KEY = "wKpIUIIREpwp9a613Cii"

# จากโค้ดตัวอย่างในหน้า Deploy
WORKSPACE_NAME = "max-abkdo"  # ถ้าในตัวอย่างเขียนชื่ออื่น ให้เปลี่ยนตามนั้น
WORKFLOW_ID = "detect-count-and-visualize-4"  # ดูจากโค้ดตัวอย่างในข้อ 3

# สร้าง client เอาไว้เรียก workflow
client = InferenceHTTPClient(
    api_url=API_URL,
    api_key=API_KEY,
)

# -------------------------
# เสิร์ฟหน้าเว็บ
# -------------------------
@app.route("/")
def serve_frontend():
    return send_from_directory("../frontend", "peoplecounterai_web.html")


# -------------------------
# เรียก workflow เพื่อนับคน
# -------------------------
@app.route("/count-people", methods=["POST"])
def count_people():
    # เช็กว่ามีไฟล์อัปโหลดมาหรือยัง
    if "image" not in request.files:
        return jsonify({"error": "no_image_uploaded"}), 400

    uploaded_file = request.files["image"]

    # เซฟไฟล์ชั่วคราวแล้วส่ง path ให้ workflow
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        uploaded_file.save(tmp)
        temp_path = tmp.name

    try:
        # เรียก workflow ของเรา
        result = client.run_workflow(
            workspace_name=WORKSPACE_NAME,
            workflow_id=WORKFLOW_ID,
            images={
                "image": temp_path  # path ไปยังไฟล์รูปที่เซฟไว้
            },
            use_cache=True,
        )

        # ดูผลลัพธ์ใน terminal
        print("WORKFLOW RESULT =", result)

        # โครงสร้างผลลัพธ์ของ Detect, Count, and Visualize
        # มักจะเป็น list มี 1 element: [ { "count_objects": ..., "output_image": ... } ]
        item = result[0] if isinstance(result, list) and len(result) > 0 else result

        people_count = (
            item.get("count_objects")
            or item.get("people_count")
            or 0
        )

        # รูปผลลัพธ์ (มีกรอบ)
        image_data = (
            item.get("output_image")
            or item.get("image_data")
            or None
        )

        # ถ้ารูปไม่ได้มี prefix data:image/... ให้เติมให้เอง
        if image_data and not str(image_data).startswith("data:"):
            image_data = "data:image/jpeg;base64," + str(image_data)

        return jsonify({
            "people_count": int(people_count),
            "image_data": image_data
        })

    except Exception as e:
        print("ERROR CALLING WORKFLOW:", e)
        return jsonify({"error": "workflow_failed"}), 500

    finally:
        # ลบไฟล์ชั่วคราวออก
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)