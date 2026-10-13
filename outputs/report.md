# Báo cáo GPU FinOps — Lê Hoàng Thiên Phú

Mã học viên: 2A202602908 

## Cách thực hiện và phạm vi

M1–M5 đã được chạy trên local với dataset tất định của lab. Đây là kết quả mô phỏng, không phải hóa đơn cloud hay phép đo GPU thật. Vì seed cố định, số liệu có thể giống bản mẫu dù đã chạy lại.

M5 chạy bằng `.venv/bin/python missions/m5_report.py` với matplotlib 3.9.4 cài trong repo. `savings.png` được sinh lại lúc 12:01:23 (UTC+7), dung lượng 35.862 bytes. Báo cáo này được biên tập từ kết quả terminal; chạy lại M5 sẽ ghi đè phần phân tích bằng báo cáo tự động.

## Baseline vs. optimized

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
- Cheapest+cleanest region: europe-north1

_Figures are June-2026 as-of snapshots; re-baseline before acting._

## Phân tích kết quả M1–M4

- M1: `gpu-h100-4` có GPU-Util 98.2% nhưng MFU 19.4%; `gpu-a10g-1` có GPU-Util 96.9% nhưng MFU 26.8%. GPU bận không đồng nghĩa sử dụng hiệu quả FLOPs. Cần profiling để xác định nguyên nhân; telemetry này chưa chứng minh memory stall hay kernel overhead. Idle waste là $20/ngày, tương đương $600 trong 30 ngày.
- M2: 2.400 request, 7.533.027 token. Baseline $48.87/ngày và $6.488/1M-token; optimized $8.48/ngày và $1.126/1M-token, giảm 82.6%. Đây là đơn giá inference, không phải đơn giá cho toàn bộ chi phí training và inference M5.
- M3: on-demand $25,667/tháng; optimized $15,627/tháng, giảm 39.1%. Policy có cả spot và reserved. Với discount giả định 45%, break-even utilization là 55%; cần kiểm tra interruption và thời hạn cam kết trước khi áp dụng thực tế.
- M4: tag coverage khoảng 92%, chargeback ready theo gate 80% của lab. Chi phí/ngày: assistant $2.59, search $2.49, eval $1.79, rag $1.60. FOCUS export chứa mẫu 50 request đầu tiên, được sắp theo team/project để dễ rà soát; không phải toàn bộ 2.400 request, nên tổng CSV không đại diện tổng chi phí M4.

## Khuyến nghị cho NimbusAI

1. Tự động tắt idle GPU sau khi job hoàn thành để giảm lãng phí dễ nhận diện.
2. Ưu tiên rà soát purchasing vì đóng góp savings lớn nhất ($10,040/tháng); chọn spot cho job chịu gián đoạn và reserved theo mức sử dụng thực tế.
3. Áp dụng cascade/cache/batch cùng kiểm soát chất lượng và latency. Theo dõi $/1M-token theo team, cập nhật tag trước khi chargeback.

Right-sizing $655 là ước tính của M5; cần kiểm tra VRAM và hiệu năng trước khi thay GPU. Vùng europe-north1 tốt nhất theo bảng giả định của lab, nhưng triển khai còn phụ thuộc latency và nơi lưu dữ liệu. Các lever được làm tròn riêng nên tổng bảng có thể lệch $1 so với savings tổng.

## Trạng thái kiểm tra

Đã chạy M1–M5 và sinh lại ảnh local. Chưa xác nhận verify 11/11 và pytest 15/15 trong môi trường hiện tại.
