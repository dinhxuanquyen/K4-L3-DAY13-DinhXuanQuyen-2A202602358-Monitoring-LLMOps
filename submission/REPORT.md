# Báo cáo cá nhân — K4-L3A Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Đinh Xuân Quyền
- **MSSV:** 2A202602358
- **Lớp:** K4-L3A
- **Repository URL:** https://github.com/dinhxuanquyen/K4-L3-DAY13-DinhXuanQuyen-2A202602358-Monitoring-LLMOps
- **Commit SHA cuối:**
- **Challenge ID:**
- **Tên project Langfuse cá nhân:** `day13-k4-l3a-2A202602358`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence            | Đường dẫn                             |
| ------------------- | ------------------------------------- |
| Pytest cuối         | `evidence/01-pytest.png`              |
| Log validator       | `evidence/02-log-validator.png`       |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log      | `evidence/04-structured-log.png`      |
| PII redaction       | `evidence/05-pii-redaction.png`       |
| Trace list          | `evidence/06-trace-list.png`          |
| Trace waterfall     | `evidence/07-trace-waterfall.png`     |
| Trace metadata      | `evidence/08-trace-metadata.png`      |
| Prompt versions     | `evidence/09-prompt-versions.png`     |
| Prompt rollback     | `evidence/10-prompt-rollback.png`     |
| Dashboard runtime   | `evidence/11-dashboard-overview.png`  |
| Incident metric     | `evidence/12-incident-metric.png`     |
| Incident log        | `evidence/13-incident-log.png`        |
| Incident trace      | `evidence/14-incident-trace.png`      |

## 3. Kết quả kỹ thuật

| Nội dung                | Baseline  | Kết quả cuối | Nhận xét                                                                 |
| ----------------------- | --------- | ------------ | ------------------------------------------------------------------------ |
| `validate_logs.py`      | 30/100    | 100/100      | Đã có correlation ID, đủ required fields, log enrichment và PII scrubber |
| `validate_dashboard.py` | 6/6       | 6/6          | Dashboard contract đủ 6 panel, có time range, đơn vị và threshold        |
| `pytest`                | 22 passed | 26 passed    | Test tracing/prompt, dashboard, logging, PII và metrics đều pass         |
| Số traces hợp lệ        |           |              |                                                                          |
| Số PII leak             |           |              |                                                                          |
| Latency P95 / TTFT P95  |           |              |                                                                          |
| Retrieval success rate  |           |              |                                                                          |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** `correlation_id` được trích xuất từ header `x-request-id`, nếu không có sẽ tự sinh ngẫu nhiên định dạng `req-<8-hex>`. Sau đó bind vào `structlog.contextvars` và gán vào `request.state`.
- **Các metadata được ghi vào structured log:** `user_id_hash`, `session_id`, `feature`, `model`, `env`, và `correlation_id`.
- **Cách bảo đảm PII được scrub trước khi ghi:** Hàm `scrub_event` sử dụng RegEx để che (redact) PII được đăng ký trong danh sách `processors` của `structlog`, chạy trước khi log được parse sang JSON hay ghi vào file.
- **Cách kiểm chứng kết quả:** Chạy test `validate_logs.py` trên file `data/logs.jsonl` đảm bảo đủ field, đủ correlation ID và không có PII leak.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** File `.env` chứa Langfuse Secret/Public Key cá nhân, do đó mọi trace tự động được đẩy về đúng project `day13-k4-l3a-2A202602358` trên Langfuse Cloud.
- **Cấu trúc root/retrieval/generation observations:** Có 1 root trace (`lab-agent-run`) bao bọc lấy 2 child observations: `retrieval` (loại span) và `llm_call` (loại generation có cost/token usage).
- **Cách nối trace với log:** Gán chung `correlation_id` (ví dụ: `req-xxxx`) vào structured log qua `bind_contextvars` và vào Langfuse trace metadata qua `propagate_attributes(metadata={"correlation_id": ...})`.
- **Prompt name:** `day13-chat`
- **Version/label baseline:** Version 1 (`baseline`)
- **Version/label candidate:** Version 2 (`candidate`)
- **Trace ID của mỗi version:** (Bạn hãy copy 2 Trace ID thực tế từ Langfuse paste vào đây)
- **Cách promote và rollback `production`:** Trên UI Langfuse -> vào Prompts -> Chọn version mới -> Add label "production" để promote. Khi có lỗi, xóa label "production" ở version hiện tại và add lại "production" vào version 1 để rollback.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** Được định nghĩa bằng file `config/dashboard.yaml` trích xuất thông tin từ structured logs JSONL (gồm Latency, Traffic, Errors, Cost, Tokens, Quality).
- **SLO và lý do chọn:** `fast_successful_requests` yêu cầu response thành công trong không quá 3000 ms trên cửa sổ 28 ngày; target là 99.5%. Đây là SLI theo request, không đồng nghĩa với P95 <= 3 giây.
- **Cách tính error budget:** `100% - 99.5% = 0.5%` số request được phép không đạt SLI trong cửa sổ 28 ngày; đây không phải ngân sách downtime.
- **Ba alert và runbook tương ứng:** (1) `High_Latency_P95` (P95 > 3000 ms), (2) `Elevated_Error_Rate` (error rate > 2%), (3) `Cost_Spike` (daily cost > $2.5). Điều kiện, thời gian duy trì và runbook nằm trong `config/alert_rules.yaml` và `docs/alerts.md`.

## 7. Điều tra challenge

- **Challenge ID:**
- **Khoảng thời gian điều tra:**
- **Triệu chứng từ metrics:**
- **Log line và correlation ID liên quan:**
- **Trace ID và span gây ảnh hưởng:**
- **Root cause:**
- **Fix action:**
- **Preventive measure:**

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:**
- **Một lỗi/blocker đã gặp:**
- **Cách tìm nguyên nhân và xử lý:**
- **Cách hiểu luồng Metrics → Logs → Traces:**
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:**
- **Điều quan trọng nhất đã học:**
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:**

## 9. Checklist trước khi nộp

- [ ] Kết quả và evidence thuộc commit SHA cuối.
- [ ] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [ ] Incident evidence nối đúng metric → log → trace.
- [ ] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [ ] Repository chạy lại được theo README.
- [ ] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
