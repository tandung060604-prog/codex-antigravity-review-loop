# Chi phí, quota và rủi ro

## Hai đồng hồ chi phí

Skill dùng hai hệ thống khác nhau:

1. **Codex context/token:** dùng khi Codex đọc prompt, state, diff, log và thực hiện review.
2. **Antigravity quota/AI credits:** dùng mỗi lần gọi `agy` và mỗi vòng Antigravity sửa code.

Không thể quy đổi cố định một yêu cầu thành một số token/credit vì còn phụ thuộc model, kích thước repo, độ khó và lượng output.

## Cách giảm chi phí thực tế

- Đối chiếu hằng ngày bằng `codex-longrun` ở chế độ chỉ đọc; không gọi AGY nếu chưa có task cần sửa.
- Chia việc lớn thành task `READY` nhỏ có acceptance criteria.
- Đặt 1–2 vòng cho bug/feature nhỏ; chỉ dùng 5 vòng khi task thực sự cần.
- Yêu cầu AGY trả block trạng thái ngắn, không dán toàn bộ log.
- Review diff và chạy test mục tiêu trước suite đầy đủ.
- Không dùng `--continue` mặc định vì có thể kéo theo context cũ.
- Dừng sau hai vòng không tiến triển thay vì tiếp tục tiêu quota.
- Dùng `$ponytail` để ưu tiên code/dependency đang có.

## Rủi ro chính

| Rủi ro | Dấu hiệu | Biện pháp |
| --- | --- | --- |
| Chạy sai project | diff xuất hiện ngoài phạm vi | xác nhận cwd và baseline trước khi giao |
| Tin vào báo cáo AGY | AGY nói DONE nhưng test/UI chưa chứng minh | Codex review diff, test và localhost độc lập |
| Vòng lặp vô hạn | cùng lỗi lặp lại | giới hạn vòng và stop sau 2 vòng không tiến triển |
| Hỏng thay đổi sẵn có | file cũ bị ghi đè | không reset/clean; phân biệt pre-existing diff |
| Lộ thông tin | token trong prompt/log/state | redact, không lưu secret vào repo public |
| Hành động ngoài ý muốn | commit/deploy/mua credit | mặc định chặn, yêu cầu xác nhận riêng |
| UI chưa đủ chất lượng | build pass nhưng motion giật/không accessible | kiểm tra browser, console và prefers-reduced-motion |
| State lỗi thời | HANDOFF không khớp Git | cập nhật bằng command/result thực tế và phân loại UNKNOWN |

## Quyết định an toàn

Khi gặp credentials, quyền mới, migration phá dữ liệu, production deploy, thay đổi billing hoặc xóa file hàng loạt, hãy dừng và hỏi người dùng. Skill không được dùng để bypass quyền, quota hoặc chính sách tài khoản.
