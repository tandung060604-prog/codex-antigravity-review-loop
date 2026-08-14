# Đối chiếu hằng ngày

Skill không chạy nền. Chỉ đối chiếu khi người dùng mở Codex và yêu cầu; không gọi Antigravity cho việc chỉ đọc trạng thái.

## Đầu ngày

```text
$codex-longrun

Đối chiếu trạng thái hôm nay, chỉ đọc:
- đọc docs/agent/PROJECT_STATE.md, BACKLOG.md, HANDOFF.md nếu có;
- kiểm tra branch, git status --short --branch, diff --stat và commit gần đây;
- phân loại VERIFIED / REPORTED / INFERRED / UNKNOWN;
- tóm tắt việc đã xong, việc còn lại, blocker, rủi ro và đúng một task READY tiếp theo;
- không sửa code, không gọi Antigravity, không chạy suite tốn thời gian.
```

## Trong ngày

Chỉ gọi `$agy-review-loop` sau khi một task `READY` có acceptance criteria rõ ràng. Với task nhỏ, yêu cầu tối đa 1–2 vòng và ghi rõ lệnh kiểm thử.

## Cuối ngày

```text
$codex-longrun

Cập nhật checkpoint bằng bằng chứng thực tế: file đổi, command/result, task DONE/REVIEW/BLOCKED, rủi ro, task READY kế tiếp và lệnh đầu tiên cho phiên sau.
```

Nếu state không có bằng chứng command/result, phân loại là `UNKNOWN`, không coi là hoàn tất.
