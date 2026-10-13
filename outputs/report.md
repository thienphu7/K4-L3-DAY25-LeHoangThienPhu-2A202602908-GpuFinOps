# NimbusAI — GPU Cost Optimization Report

**Period:** monthly  
**Baseline spend:** $27,133  
**Optimized spend:** $14,626  
**Projected savings:** $12,507  (**46%**)

## Savings by lever

| Lever | Savings (USD) |
|---|---|
| Inference (cascade/cache/batch) | $1,212 |
| Purchasing (spot/reserved) | $10,040 |
| Right-size util-lies | $655 |
| Kill idle GPUs | $600 |

## Sustainability

- Energy per query: 0.24 Wh
- Carbon per query: 0.091 gCO2e
- Cleanest region (catalog): europe-north1

_Figures are June-2026 as-of snapshots; re-baseline before acting._

# GPU FinOps — Lê Hoàng Thiên Phú (2A202602908)

## Cách làm và kết quả

M1–M5 được chạy local trên dataset seed=25 của đề. Các số liệu mô phỏng có thể trùng bản mẫu; biểu đồ được sinh bằng matplotlib trong .venv của repo. Không cần GPU thật hay API key. Báo cáo tự động và phân tích cá nhân được ghép khi chạy M5 để không mất nội dung khi verify/pytest chạy lại pipeline.

Baseline tổng hợp khoảng $27,133/tháng, optimized $14,626, savings khoảng 46%. Riêng inference M2 giảm từ $6.488 xuống $1.126/1M-token (82.6%). Đây là đơn giá inference, không phải đơn giá của cả training. Purchasing đóng góp lớn nhất khoảng $10,040/tháng, tiếp theo inference $1,212, right-sizing $655, idle $600. Các số hiển thị làm tròn nên có thể lệch $1 khi cộng bảng.

## GPU-Util lie và tác động

gpu-h100-4 có GPU-Util 98.2% nhưng MFU 19.4%; gpu-a10g-1 có utilization 96.9% nhưng MFU 26.8%. Utilization đo thời gian GPU hoạt động, không đo FLOPs hiệu quả. Cần profiling để phân biệt memory stall, kernel overhead hay nguyên nhân khác; dataset không chứng minh nguyên nhân cụ thể. Không thể coi mọi FLOPs chưa dùng là tiền có thể thu hồi trực tiếp. Idle waste đo được trong mô phỏng là $20/ngày, tương đương $600/30 ngày. Right-sizing của M5 là ước tính, cần xác nhận VRAM và latency trước khi áp dụng.

## Phần mở rộng

Ngân sách reasoning: tách số request, USD và Wh theo is_reasoning; mô phỏng cap 10% traffic, chuyển phần dư sang small/non-reasoning, giữ nguyên số token. Hệ số 80× chỉ áp dụng cho năng lượng, không tự nhân giá USD. Dataset thiếu confidence nên dùng first-N làm proxy; policy thực tế cần kiểm tra chất lượng và routing theo độ khó. Kết quả định lượng nằm trong extensions_report.md và extensions_results.json.

Carbon-aware scheduling: tính rated watts × GPU-hours cho từng job interruptible, so sánh năm vùng về tiền điện và carbon. europe-north1 sạch nhất nhưng us-east-wa rẻ điện nhất. Tiền điện không phải giá thuê GPU và không cộng thêm vào savings M5. Chọn vùng theo ưu tiên carbon/chi phí, kiểm tra latency, transfer và data residency. Đây là giả định năng lượng ở rated power, không phải phép đo điện.

## Khuyến nghị ưu tiên

1. Tự động tắt GPU idle sau khi job hoàn thành và theo dõi GPU-hours không phục vụ workload.
2. Kiểm tra duty cycle trước khi mua reserved; dùng spot cho job có checkpoint và chịu được interruption. Purchasing có ROI lớn nhất theo mô hình.
3. Triển khai cascade/cache/batch kèm kiểm tra chất lượng, latency và $/1M-token theo team. Tag coverage khoảng 92% vượt gate 80% trong lab nhưng vẫn cần xử lý request thiếu tag khi chargeback thực tế.

FOCUS CSV chỉ là mẫu 50 request, không đại diện tổng 2.400 request. Bonus tracker là mock, model CPU đo throughput thật nhưng giá CPU giả định, exporter dùng telemetry tổng hợp. Kết quả bonus và kiểm tra tự động được lưu riêng, không coi exit 0 do skip là benchmark thành công.


## Your Turn — kết quả định lượng

### Ngân sách Reasoning

Reasoning: 8.38% traffic, 16.46% chi phí.

| Traffic | Requests | USD | Wh |
|---|---:|---:|---:|
| reasoning | 201 | 1.3965 | 29787.74 |
| normal | 2199 | 7.0882 | 1887.56 |

Cap 10% traffic: chuyển 0 request sang small/non-reasoning. Chi phí $8.4846 → $8.4846; năng lượng 31675.31 → 31675.31 Wh.
Giả định token không đổi, hệ số năng lượng reasoning 80× của lab. Dataset thiếu confidence: giữ N request đầu là proxy; policy thực tế cần confidence và đánh giá chất lượng.

Sensitivity cap 5%: chuyển 81 request; USD 8.4846 → 8.0302, Wh 31675.31 → 20311.32. Cap 10% không có tác động vì traffic hiện tại chỉ 8,38%; không giả định savings khi chưa chạm cap.

### Carbon-aware scheduling

| Region | USD/kWh | gCO2/kWh | Electricity USD | Carbon g |
|---|---:|---:|---:|---:|
| us-east-1 | 0.12 | 380 | 214.68 | 679820.00 |
| us-west-2 | 0.07 | 120 | 125.23 | 214680.00 |
| europe-north1 | 0.09 | 30 | 161.01 | 53670.00 |
| europe-central2 | 0.18 | 660 | 322.02 | 1180740.00 |
| us-east-wa | 0.055 | 90 | 98.39 | 161010.00 |

Sạch nhất: europe-north1; rẻ điện nhất: us-east-wa. Chuyển job interruptible từ us-east-1 sang vùng sạch nhất giảm 626150.00 gCO2e và $53.67 tiền điện.
Ước tính dùng rated watts × GPU-hours, không phải điện đo thực tế. Tiền điện không được cộng lại vào savings thuê GPU. Có trade-off latency, transfer và data residency; không có một vùng vừa rẻ nhất vừa sạch nhất trong catalog.


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
