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
