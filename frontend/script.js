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

  // 2) เตรียม FormData
  const formData = new FormData();
  formData.append('image', fileInput.files[0]);

  // 3) แสดงสถานะ
  resultDiv.innerText = 'กำลังประมวลผล...';
  outputImage.style.display = 'none';

  try {
    // ✅ ใช้ relative path (สำคัญมาก)
    const response = await fetch('/count-people', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    console.log('DATA จาก backend = ', data);

    // 🔹 กรณี AI ยังปิดอยู่ (demo mode)
    if (data.message) {
      resultDiv.innerHTML =
        '⚠️ <b>โหมดสาธิต (Demo)</b><br>ระบบ AI ปิดชั่วคราว';
      return;
    }

    const count = data.people_count ?? 0;
    resultDiv.innerText = `ผลการตรวจจับ: พบ ${count} คนในภาพ`;

    if (data.image_data) {
      outputImage.src = data.image_data;
      outputImage.style.display = 'block';
    }

  } catch (err) {
    console.error(err);
    resultDiv.innerText = 'ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้';
  }
}
