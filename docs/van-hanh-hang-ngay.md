# Vận hành hằng ngày

## Mục tiêu

Mỗi ngày cần biết chính xác:

- hôm qua đã thay đổi file nào;
- kiểm thử nào đã chạy và kết quả;
- task nào còn dang dở;
- blocker/rủi ro nào còn mở;
- task `READY` nhỏ nhất tiếp theo là gì.

Skill không tự chạy nền. Điều này tránh sửa code hoặc tiêu quota khi bạn không có mặt. Bạn có thể chạy đối chiếu theo yêu cầu trong Codex hoặc tự tạo automation riêng sau này.

## Chuẩn bị một project dài hạn

Trong project, dùng profile Standard của `codex-longrun`:

```text
docs/agent/PROJECT_STATE.md
docs/agent/BACKLOG.md
docs/agent/HANDOFF.md
```

Không ghi token, API key, log production chưa lọc hoặc dữ liệu khách hàng vào các file này.

## Đầu ngày

Gửi nguyên văn hoặc điều chỉnh prompt sau:

```text
$codex-longrun

Đối chiếu trạng thái đầu ngày, chỉ đọc:
1. đọc docs/agent/PROJECT_STATE.md, BACKLOG.md, HANDOFF.md nếu có;
2. kiểm tra branch, git status --short --branch, diff --stat và commit gần đây;
3. phân loại bằng chứng VERIFIED / REPORTED / INFERRED / UNKNOWN;
4. tóm tắt: đã hoàn tất, chưa hoàn tất, blocker, rủi ro và task READY tiếp theo;
5. không sửa code, không gọi Antigravity, không chạy suite tốn thời gian.
```

Đối chiếu chỉ đọc thường không cần gọi `$agy-review-loop`, nên tiết kiệm quota.

## Trong ngày

Chỉ giao một task `READY` mỗi lần:

```text
$agy-review-loop

Thực hiện task READY: [mục tiêu ngắn].

Acceptance criteria:
- [tiêu chí quan sát được];
- [test/lint/build cần đạt];
- [phạm vi không được vượt].

Áp dụng nguyên tắc $ponytail. Tối đa 2 vòng Antigravity. Không commit, push, deploy.
```

Task UI phải có kiểm tra localhost và console; task backend phải có regression test hoặc lệnh tái hiện rõ ràng.

## Cuối ngày

```text
$codex-longrun

Cập nhật checkpoint bằng bằng chứng thực tế:
- file đã thay đổi và lý do;
- lệnh kiểm thử đã chạy và kết quả chính xác;
- task đã DONE/REVIEW/BLOCKED;
- rủi ro và giả định còn lại;
- task READY kế tiếp;
- lệnh đầu tiên cho phiên sau.
```

## Báo cáo tối thiểu nên nhận được

```text
Ngày: YYYY-MM-DD
Đã hoàn tất: ...
Đang làm: ...
Kiểm thử: ...
Blocker: NONE hoặc ...
Rủi ro: ...
Task READY tiếp theo: ...
```

Nếu báo cáo thiếu command/result thực tế, coi đó là `UNKNOWN`, không coi là đã hoàn tất.
