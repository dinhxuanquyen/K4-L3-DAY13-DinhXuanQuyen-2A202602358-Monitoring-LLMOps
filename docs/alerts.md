# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## High-Latency

- Tên: High_Latency_P95
- Severity: warning
- Duration: 5m
- Kênh thông báo: Slack `#llmops-alerts` (đổi thành channel của workspace cá nhân nếu cần)
- SLI/SLO liên quan: `fast_successful_requests` (latency <= 3000ms)
- Điều kiện và thời gian duy trì: `p95_latency_ms > 3000` duy trì trong 5 phút.
- Ảnh hưởng tới người dùng: Người dùng phải chờ đợi quá lâu để nhận được phản hồi, làm giảm UX.
- Ba bước kiểm tra đầu tiên:
  1. Xem dashboard để kiểm tra số lượng request hiện tại có tăng vọt không (traffic spike).
  2. Mở `data/logs.jsonl`, lấy `correlation_id` của request bị chậm.
  3. Lên Langfuse tìm trace ID tương ứng, xem span nào (retrieval hay generation) mất nhiều thời gian nhất.
- Mitigation tạm thời: Bật tính năng caching hoặc scale-up số lượng instance của service nếu do quá tải.
- Owner: dev_team

## Elevated-Error-Rate

- Tên: Elevated_Error_Rate
- Severity: critical
- Duration: 5m
- Kênh thông báo: Slack `#llmops-alerts` (đổi thành channel của workspace cá nhân nếu cần)
- SLI/SLO liên quan: `error_rate_pct_max` (error rate <= 2%)
- Điều kiện và thời gian duy trì: `error_rate_pct > 2` duy trì trong 5 phút.
- Ảnh hưởng tới người dùng: Một lượng lớn người dùng nhận được lỗi thay vì câu trả lời, làm cạn kiệt Error Budget nhanh chóng.
- Ba bước kiểm tra đầu tiên:
  1. Xem panel lỗi trên dashboard để xem loại lỗi (ví dụ: `TimeoutError`, `RateLimitError`).
  2. Lọc `data/logs.jsonl` với `event == "request_failed"` để xem `error_type` và message lỗi chi tiết.
  3. So sánh với biểu đồ traffic xem có bị tấn công DDoS không.
- Mitigation tạm thời: Rollback phiên bản prompt mới nhất nếu có thay đổi gần đây, hoặc fallback sang model AI dự phòng/kích hoạt rate limiting cứng.
- Owner: dev_team

## Cost-Spike

- Tên: Cost_Spike
- Severity: warning
- Duration: 5m
- Kênh thông báo: Slack `#llmops-alerts` (đổi thành channel của workspace cá nhân nếu cần)
- SLI/SLO liên quan: `daily_cost_usd_max`
- Điều kiện và thời gian duy trì: `daily_cost_usd > 2.5` duy trì trong 5 phút.
- Ảnh hưởng tới người dùng: Không ảnh hưởng tới người dùng ngay lập tức, nhưng gây lãng phí tài chính nghiêm trọng cho công ty.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra số lượng input/output tokens trên dashboard xem có bất thường không.
  2. Xem trace trên Langfuse để xem LLM có bị vòng lặp vô tận (infinite loop) hoặc prompt quá lớn không.
  3. Xem logs xem có IP/User nào đang spam request không.
- Mitigation tạm thời: Block IP của user đang spam, hoặc giới hạn `max_tokens` của LLM xuống mức thấp hơn.
- Owner: dev_team
