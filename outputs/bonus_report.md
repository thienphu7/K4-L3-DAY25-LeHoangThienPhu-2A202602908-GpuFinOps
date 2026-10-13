## Bonus — kết quả chạy local ngày 13/10/2026

| Bonus | Kết quả | Bằng chứng |
|---|---|---|
| LiteLLM-style tracker | 10 chat request được nhận, request tiếp theo bị chặn trước khi vượt cap $0.05; chat spend khoảng $0.046, eval khoảng $0.0003; 15 request được log. | bonus_tracker.log |
| Local CPU model | sshleifer/tiny-gpt2 sinh 64 token sau warm-up; khoảng 0.05 giây, 1.340,4 token/giây trong lần chạy này. | bonus_local_model.log |
| Observability | HTTP scrape /metrics trả 200; có MFU/utilization/hourly cost/wasted-FLOPs cost cho 11 GPU. | bonus_exporter.prom, bonus_results.json |

Tracker dùng backend mock, không gọi LiteLLM/provider thật. CPU throughput được đo thật nhưng rất nhỏ và nhạy với nhiễu thời gian; giá khoảng $0.02/1M output tokens dùng CPU rate giả định $0.10/giờ. Không so sánh chất lượng tiny-gpt2 với model inference của lab, không coi tiền điện hay giá CPU giả định là hóa đơn thực tế.

Máy chưa có Docker nên observability chạy theo phương án pure-Python của README. Prometheus và Grafana containers/dashboard chưa được chạy. Giá wasted-FLOPs là proxy `(1-MFU)*hourly price`, không phải khoản tiết kiệm được đảm bảo.

## Xác nhận kiểm tra

- verify.py: 11/11 checks passed.
- pytest: 17 passed, gồm 15 test gốc và 2 test extension; test gốc không bị sửa.
- Hai extension đã triển khai: reasoning budget và carbon-aware scheduling.
- Các mô hình chi phí/carbon dùng catalog snapshot của đề, không dùng giá thị trường hiện tại.
