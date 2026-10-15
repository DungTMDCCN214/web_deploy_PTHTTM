// Hàm dùng chung. Các trang bài toán gọi postJson để nói chuyện với Spring Boot.
async function postJson(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error('Máy chủ trả về mã ' + res.status);
  return res.json();
}
