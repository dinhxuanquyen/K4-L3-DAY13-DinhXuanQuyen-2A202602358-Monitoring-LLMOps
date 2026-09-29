# Báo cáo cá nhân — K4-L3A Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Đinh Xuân Quyền
- **MSSV:** 2A202602358
- **Lớp:** K4-L3A
- **Repository URL:** https://github.com/dinhxuanquyen/K4-L3-DAY13-DinhXuanQuyen-2A202602358-Monitoring-LLMOps
- **Commit SHA cuối:**
- **Challenge ID:** `day13-k4-l3a-monitoring-llmops-v1`
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
| `pytest`                | 22 passed | 27 passed    | Test tracing/prompt, dashboard, logging, PII và metrics đều pass         |
| Số traces hợp lệ        |           | >= 10        | Langfuse trace list có nhiều root traces `lab-agent-run` do workload tạo |
| Số PII leak             |           | 0            | `validate_logs.py` không phát hiện PII leak                              |
| Latency P95 / TTFT P95  |           | 2654 / 50 ms | Giá trị trong lúc chạy CP3 challenge `rag_slow`                          |
| Retrieval success rate  |           | 100%         | Incident là latency, không phải retrieval failure                         |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** `correlation_id` được trích xuất từ header `x-request-id` nếu header đúng định dạng `req-<8-hex>`; nếu không có hoặc sai định dạng thì tự sinh ID mới. Sau đó bind vào `structlog.contextvars`, gán vào `request.state`, và trả lại qua response header.
- **Các metadata được ghi vào structured log:** `user_id_hash`, `session_id`, `feature`, `model`, `env`, và `correlation_id`.
- **Cách bảo đảm PII được scrub trước khi ghi:** Hàm `scrub_event` sử dụng RegEx để che (redact) PII được đăng ký trong danh sách `processors` của `structlog`, chạy trước khi log được parse sang JSON hay ghi vào file.
- **Cách kiểm chứng kết quả:** Chạy test `validate_logs.py` trên file `data/logs.jsonl` đảm bảo đủ field, đủ correlation ID và không có PII leak.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** File `.env` chứa Langfuse Secret/Public Key cá nhân, do đó mọi trace tự động được đẩy về đúng project `day13-k4-l3a-2A202602358` trên Langfuse Cloud.
- **Cấu trúc root/retrieval/generation observations:** Có 1 root trace (`lab-agent-run`) bao bọc lấy 2 child observations: `retrieval` (loại retriever, có query preview đã scrub và `doc_count`) và `llm-generate` (loại generation, có model, cost/token usage và answer preview).
- **Cách nối trace với log:** Gán chung `correlation_id` (ví dụ: `req-xxxx`) vào structured log qua `bind_contextvars` và vào Langfuse trace metadata qua `propagate_attributes(metadata={"correlation_id": ...})`.
- **Prompt name:** `day13-chat`
- **Version/label baseline:** Version 1 (`baseline`)
- **Version/label candidate:** Version 3 (`candidate`)
- **Trace ID của mỗi version:** (Bạn hãy copy 2 Trace ID thực tế từ Langfuse paste vào đây)
- **Cách promote và rollback `production`:** Trên UI Langfuse -> vào Prompts -> Chọn version mới -> Add label "production" để promote. Khi có lỗi, xóa label "production" ở version hiện tại và add lại "production" vào version 1 để rollback.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** Được định nghĩa bằng file `config/dashboard.yaml` trích xuất thông tin từ structured logs JSONL (gồm Latency, Traffic, Errors, Cost, Tokens, Quality).
- **SLO và lý do chọn:** `fast_successful_requests` yêu cầu response thành công trong không quá 3000 ms trên cửa sổ 28 ngày; target là 99.5%. Đây là SLI theo request, không đồng nghĩa với P95 <= 3 giây.
- **Cách tính error budget:** `100% - 99.5% = 0.5%` số request được phép không đạt SLI trong cửa sổ 28 ngày; đây không phải ngân sách downtime.
- **Ba alert và runbook tương ứng:** (1) `High_Latency_P95` (P95 > 3000 ms), (2) `Elevated_Error_Rate` (error rate > 2%), (3) `Cost_Spike` (daily cost > $2.5). Điều kiện, thời gian duy trì và runbook nằm trong `config/alert_rules.yaml` và `docs/alerts.md`.

## 7. Điều tra challenge

- **Challenge ID:** `day13-k4-l3a-monitoring-llmops-v1`
- **Khoảng thời gian điều tra:** 2026-09-29 10:00:13Z đến 2026-09-29 10:00:26Z.
- **Triệu chứng từ metrics:** Latency P95 tăng lên khoảng 2654 ms, vượt ngưỡng challenge 2000 ms; error rate vẫn 0%, retrieval success rate 100%, TTFT P95 khoảng 51 ms.
- **Log line và correlation ID liên quan:** `data/logs.jsonl` dòng 380-381, `correlation_id=req-abb68491`, event `response_sent` có `latency_ms=2654`, `feature=monitoring`, `tool_name=retrieval`, `tool_success=true`.
- **Trace ID và span gây ảnh hưởng:** Tìm trace trên Langfuse bằng metadata `correlation_id=req-abb68491`; span gây ảnh hưởng là `retrieval` do incident `rag_slow` làm bước truy xuất chậm. Trace ID thật cần copy từ Langfuse sau khi mở trace tương ứng.
- **Root cause:** Retrieval layer bị làm chậm giả lập bởi incident `rag_slow`, khiến latency request vượt ngưỡng trong khi generation/TTFT và error rate không bất thường.
- **Fix action:** Tắt incident `rag_slow`, kiểm tra lại vector store/retrieval backend, thêm timeout/caching hoặc fallback cho retrieval khi latency vượt ngưỡng.
- **Preventive measure:** Alert theo P95 latency và theo retrieval span duration, dashboard hiển thị latency/TTFT/retrieval success, runbook yêu cầu đi từ Metrics → Logs → Traces bằng `correlation_id`.

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** Không capture raw input/output tự động trong Langfuse observations để giảm rủi ro lộ PII; thay vào đó chủ động ghi input/output preview đã scrub cùng metadata, token/cost và `correlation_id` để điều tra.
- **Một lỗi/blocker đã gặp:** Khi tìm trace theo `correlation_id`, nếu filter sai key thành `metadata.req-...` thì Langfuse không trả kết quả; key đúng là `metadata.correlation_id`.
- **Cách tìm nguyên nhân và xử lý:** Dùng dashboard/metrics xác định latency P95 vượt ngưỡng, lấy `correlation_id` từ log chậm, rồi mở trace cùng ID trên Langfuse để xác định span `retrieval` là bước gây chậm.
- **Cách hiểu luồng Metrics → Logs → Traces:** Metrics cho biết triệu chứng và khoảng thời gian; logs chỉ ra request cụ thể; traces tách từng observation để khoanh vùng root cause.
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** Prompt version/label giúp biết request dùng prompt nào và rollback được khi version mới gây lỗi; token/cost giúp phát hiện cost spike; SLO/error budget giúp đánh giá mức độ ảnh hưởng thay vì chỉ nhìn một request đơn lẻ.
- **Điều quan trọng nhất đã học:** Một kết luận incident chỉ đáng tin khi metric, log và trace cùng chỉ về một nguyên nhân.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** Cần bổ sung ảnh evidence Langfuse/dashboard và copy trace ID thật vào report trước khi nộp.

## 9. Checklist trước khi nộp

- [ ] Kết quả và evidence thuộc commit SHA cuối.
- [ ] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [ ] Incident evidence nối đúng metric → log → trace.
- [ ] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [ ] Repository chạy lại được theo README.
- [ ] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
