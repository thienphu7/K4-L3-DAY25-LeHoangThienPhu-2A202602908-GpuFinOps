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
