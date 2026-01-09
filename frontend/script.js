// frontend/script.js

async function countPeople() {
  const fileInput   = document.getElementById('imageUpload');
  const resultDiv   = document.getElementById('result');
  const outputImage = document.getElementById('outputImage');

  // 1) เช็กว่ามีไฟล์ไหม
  if (!fileInput.files.length) {
    resultDiv.innerText = 'กรุณาเลือกภาพก่อนอัปโหลด';
    return;
  }

  // 2) เตรียม FormData ส่งไป backend
  const formData = new FormData();
  formData.append('image', fileInput.files[0]);

  // 3) ขณะรอผล
  resultDiv.innerText = 'กำลังประมวลผลด้วย AI...';
  outputImage.style.display = 'none';

  try {
    // 4) ยิงไปหา Flask ที่ /count-people  (ให้ตรงกับ app.py)
    const response = await fetch('http://127.0.0.1:5000/count-people', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    // 5) อ่าน JSON ตามที่ app.py ส่งกลับมา
    // { "people_count": count, "image_data": "data:image/jpeg;base64,...." }
    const data = await response.json();
    console.log('DATA จาก backend = ', data);

    const count = data.people_count ?? 0;
    resultDiv.innerText = `ผลการตรวจจับ: พบ ${count} คนในภาพ`;

    // 6) แสดงภาพผลลัพธ์ที่มีกรอบ (image_data)
    if (data.image_data) {
      outputImage.src = data.image_data;   // มี prefix data:image/jpeg;base64, มาแล้ว
      outputImage.style.display = 'block';
    }

  } catch (err) {
    console.error(err);
    resultDiv.innerText = 'เกิดข้อผิดพลาดในการประมวลผล กรุณาลองใหม่อีกครั้ง';
  }
}


