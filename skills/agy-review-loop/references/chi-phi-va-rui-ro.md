# Chi phí và rủi ro

- Codex token/context phát sinh khi đọc prompt, state, diff, log và review.
- Antigravity quota/AI credits phát sinh khi gọi `agy` và mỗi vòng sửa.

Giảm chi phí bằng cách đối chiếu hằng ngày ở chế độ chỉ đọc, chia task nhỏ, đặt 1–2 vòng cho việc nhỏ, review findings ngắn, chạy check rẻ trước và dừng sau hai vòng không tiến triển. Không hứa một con số token/credit cố định.

Rủi ro phải dừng để hỏi người dùng: sai thư mục, credential/quyền mới, migration phá dữ liệu, production deploy, mua credit, xóa hàng loạt, hoặc phát hiện secret trong prompt/log/state. Không reset/clean để che giấu thay đổi sẵn có.
