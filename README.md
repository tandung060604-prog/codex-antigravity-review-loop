# Codex Antigravity Review Loop

[![Validate](https://github.com/tandung060604-prog/codex-antigravity-review-loop/actions/workflows/validate.yml/badge.svg)](https://github.com/tandung060604-prog/codex-antigravity-review-loop/actions/workflows/validate.yml)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Public repository](https://img.shields.io/badge/repository-public-success.svg)](https://github.com/tandung060604-prog/codex-antigravity-review-loop)

Skill cho Codex để giao một nhiệm vụ lập trình cho Google Antigravity CLI (`agy`), sau đó Codex tự đối chiếu diff, kiểm thử và yêu cầu Antigravity sửa tiếp trong một số vòng giới hạn.

Skill này không thay thế Antigravity, không chứa model/API key và không vượt quota hay quyền truy cập. Nó là một lớp điều phối có kiểm soát giữa Codex và Antigravity.

**Nội dung:** [Cài đặt](#cài-đặt-nhanh) · [Dùng trong phiên](#cách-dùng-trong-mỗi-phiên-codex) · [Vận hành hằng ngày](#đối-chiếu-và-cập-nhật-hằng-ngày) · [Chi phí](#tối-ưu-token-quota-và-chi-phí) · [Rủi ro](#rủi-ro-và-cách-kiểm-soát)

## Dùng được ngay không?

Có. Bạn cần:

1. Antigravity CLI đã cài và đăng nhập: `agy --version` phải trả về phiên bản.
2. Một project Git mà Codex/Antigravity được phép đọc và sửa.
3. Một yêu cầu cụ thể với tiêu chí hoàn thành và lệnh kiểm thử.

Skill phù hợp cho bug fix, feature nhỏ–vừa, refactor có giới hạn, UI localhost, test, lint và build. Không nên giao ngay các nhiệm vụ mơ hồ, production, migration phá dữ liệu, deploy hoặc thay đổi quyền truy cập.

## Cài đặt nhanh

### Cách khuyến nghị: cài trực tiếp từ GitHub

Trong PowerShell:

```powershell
python C:\Users\<TEN_BAN>\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py `
  --repo tandung060604-prog/codex-antigravity-review-loop `
  --path skills/agy-review-loop
```

Trên macOS/Linux:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo tandung060604-prog/codex-antigravity-review-loop \
  --path skills/agy-review-loop
```

Khởi động lại Codex nếu skill chưa xuất hiện. Kiểm tra bằng cách gửi:

```text
$agy-review-loop

Hãy kiểm tra repo hiện tại và trả lời kế hoạch ngắn gọn, chưa sửa file. Không chạy Antigravity khi tôi chưa xác nhận.
```

### Clone để phát triển skill

```powershell
git clone https://github.com/tandung060604-prog/codex-antigravity-review-loop.git
cd codex-antigravity-review-loop
python scripts/validate_repo.py
python -m unittest discover -s tests -p "test_*.py"
```

Skill cài được nằm ở `skills/agy-review-loop`. Mỗi thay đổi nên được kiểm tra bằng validator trước khi push.

## Kiểm tra Antigravity trước lần chạy đầu

```powershell
agy --version
agy -p "Reply with exactly AGY_OK. Do not edit files or run commands." --output-format text
```

Nếu muốn không dùng AI credits khi quota cơ bản hết, mở Antigravity, chạy `/config` hoặc `/settings`, đặt **AI Credit Overages / Use G1 Credits = Never**. Xem quota bằng `/usage`, credit bằng `/credits`.

## Cách dùng trong mỗi phiên Codex

Không cần tự gõ lệnh `agy` trong terminal. Trong phiên đang mở đúng project, gửi một yêu cầu có mục tiêu, phạm vi và tiêu chí kiểm tra:

```text
$agy-review-loop

Trong project hiện tại, sửa lỗi validation của form đăng nhập.

Tiêu chí hoàn thành:
- xác định root cause trước khi sửa;
- thêm regression test;
- chạy lint và test liên quan;
- không đổi API công khai;
- không commit, push, deploy hoặc sửa file ngoài phạm vi.
```

Với localhost/UI:

```text
$agy-review-loop

Trong project localhost hiện tại, thêm motion tinh tế cho các khối giao diện:
- section entrance và scroll reveal;
- stagger cho card/list;
- hover/focus motion nhẹ;
- responsive desktop/mobile;
- hỗ trợ prefers-reduced-motion.

Kiểm tra stack và dependency trước, tái sử dụng thứ đã có, không rewrite ứng dụng. Kiểm tra trang localhost, console, lint, test và build. Không commit hoặc deploy.
```

Mặc định skill giới hạn tối đa 5 vòng. Với việc nhỏ, hãy nói rõ `chỉ tối đa 2 vòng` để giảm quota.

## Quy trình cho các phiên sau này

Khuyến nghị dùng ba lớp theo thứ tự:

```text
codex-longrun  →  ponytail  →  agy-review-loop  →  Antigravity CLI
```

- `codex-longrun`: quản lý task `READY`, acceptance criteria, state, checkpoint và handoff.
- `ponytail`: buộc Codex/Antigravity tìm cách đơn giản nhất, tái sử dụng code/dependency và tránh abstraction thừa.
- `agy-review-loop`: chỉ lo giao việc, review bằng chứng và lặp sửa có giới hạn.

Prompt mẫu cho task dài:

```text
$codex-longrun

Hãy đọc trạng thái bền vững trong docs/agent/ và đối chiếu Git hiện tại. Chỉ chọn một task READY.

Áp dụng nguyên tắc $ponytail cho thay đổi.
Sau khi task có acceptance criteria rõ ràng, dùng $agy-review-loop để giao task đó cho Antigravity. Giới hạn 3 vòng và dừng khi có blocker.
```

Không để Antigravity tự sửa các file state của `codex-longrun` nếu task không sở hữu chúng.

## Đối chiếu và cập nhật hằng ngày

Skill không tự chạy nền và không tự mở phiên mỗi ngày. Nó cập nhật khi bạn mở Codex và yêu cầu đối chiếu. Đây là chủ ý an toàn: không tiêu quota và không tự sửa code khi bạn vắng mặt.

Mỗi project dài hạn nên có state profile Standard của `codex-longrun`:

```text
docs/agent/PROJECT_STATE.md
docs/agent/BACKLOG.md
docs/agent/HANDOFF.md
```

Đầu ngày, gửi:

```text
$codex-longrun

Đối chiếu trạng thái hôm nay:
- đọc docs/agent/PROJECT_STATE.md, BACKLOG.md và HANDOFF.md nếu có;
- kiểm tra branch, git status, diff stat và commit gần đây;
- phân loại thông tin VERIFIED / REPORTED / INFERRED / UNKNOWN;
- tóm tắt việc đã xong, việc còn lại, blocker, rủi ro và task READY tiếp theo;
- chưa sửa code và chưa gọi Antigravity.
```

Cuối ngày, gửi:

```text
$codex-longrun

Cập nhật checkpoint hôm nay bằng bằng chứng thực tế: file đã đổi, lệnh kiểm thử và kết quả, blocker, rủi ro, task tiếp theo và lệnh đầu tiên cho phiên sau.
```

Nếu cần triển khai task trong ngày, chỉ sau bước đối chiếu mới gọi `$agy-review-loop` cho task READY đó.

## Tối ưu token, quota và chi phí

Có hai loại chi phí cần phân biệt:

| Loại | Phát sinh ở đâu | Cách giảm |
| --- | --- | --- |
| Token/context của Codex | đọc prompt, diff, log, state và review | task nhỏ, prompt tự chứa, đọc file liên quan, không dán log dài |
| Quota/AI credits của Antigravity | mỗi lần `agy` chạy và mỗi vòng sửa | giới hạn vòng, acceptance criteria rõ, chạy check có mục tiêu, dừng khi không tiến triển |

Quy tắc đã tích hợp trong skill:

- tối đa 5 vòng, và dừng sớm sau 2 vòng không tiến triển;
- không dùng `--continue` mặc định để tránh nhầm cuộc trò chuyện;
- không gọi Antigravity cho việc chỉ đọc trạng thái hằng ngày;
- chạy check rẻ nhất trước, chỉ chạy suite đầy đủ khi cần;
- gửi review dạng findings ngắn, có file và bằng chứng, không gửi lại toàn bộ lịch sử;
- không yêu cầu AGY viết báo cáo dài; chỉ cần block `AGY_STATUS / CHANGED / CHECKS / RISKS`;
- với task nhỏ, đặt giới hạn 1–2 vòng;
- tách task lớn thành nhiều task READY thay vì một prompt khổng lồ.

Không thể cam kết một con số token cố định vì chi phí phụ thuộc model, độ lớn repo, số file và độ phức tạp yêu cầu.

## Rủi ro và cách kiểm soát

| Rủi ro | Cách kiểm soát |
| --- | --- |
| AGY sửa nhầm thư mục | kiểm tra current repository và baseline trước khi giao |
| AGY báo “xong” nhưng code chưa đạt | Codex đọc diff và chạy check độc lập |
| Vòng lặp tiêu quota | giới hạn vòng, stop sau 2 vòng không tiến triển |
| UI nhìn đúng nhưng lỗi runtime | bắt buộc kiểm tra localhost và console khi làm UI |
| Mất thay đổi người dùng | ghi baseline, không reset/checkout/clean tự động |
| Lộ secret/token | không lưu secret vào state, log, prompt hoặc repo public |
| Tự ý commit/deploy/mua credit | skill chặn mặc định và yêu cầu user xác nhận |
| State hằng ngày bị cũ | dùng `codex-longrun`, ghi checkpoint bằng command/result thực tế |
| Tự động chạy khi không có mặt | skill không chạy nền; muốn lịch tự động phải thiết lập automation riêng |

## Giới hạn cần biết

- Skill không đảm bảo code đúng chỉ vì Antigravity trả `DONE`.
- Skill không thay thế review nghiệp vụ, security review hoặc QA production.
- Skill không tự động mua AI credits và không vượt hạn mức Google AI Pro.
- Skill không tự động “đối chiếu hằng ngày” nếu bạn không mở phiên hoặc thiết lập automation riêng.
- Nên dùng Guided mode của `codex-longrun` cho thay đổi lớn; chỉ dùng Autonomous mode khi bạn đã phê duyệt task.

## Phát triển và đóng góp

```powershell
python scripts/validate_repo.py
python -m unittest discover -s tests -p "test_*.py"
python C:\Users\<TEN_BAN>\.codex\skills\.system\skill-creator\scripts\quick_validate.py skills\agy-review-loop
```

Xem thêm:

- [Vận hành hằng ngày](docs/van-hanh-hang-ngay.md)
- [Chi phí và rủi ro](docs/chi-phi-va-rui-ro.md)
- [Kiến trúc](docs/architecture.md)
- [Hướng dẫn đóng góp](CONTRIBUTING.md)

## License

Apache License 2.0. Bạn có thể sử dụng, sửa đổi, tích hợp và cung cấp dịch vụ thương mại theo license. Tên dự án và thương hiệu không được dùng để tạo cảm giác được upstream chứng nhận; xem [NOTICE](NOTICE).
