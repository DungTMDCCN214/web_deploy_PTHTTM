// Bài "mnist": logic giao diện riêng.
// TODO: đọc dữ liệu từ form thật, gọi API, vẽ kết quả (biểu đồ, thanh xác suất...).
document.getElementById('run').addEventListener('click', async () => {
  const out = document.getElementById('result');
  try {
    const input = JSON.parse(document.getElementById('input').value);
    out.textContent = 'Đang xử lý...';
    const data = await postJson('/api/mnist/predict', input);
    out.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    out.textContent = 'Lỗi: ' + e.message;
  }
});
