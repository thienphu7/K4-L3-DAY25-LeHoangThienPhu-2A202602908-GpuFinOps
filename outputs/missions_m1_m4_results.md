# Mission Results: M1–M4

## M1 — Efficiency Audit

- GPU-Util lies: `gpu-h100-4`, `gpu-a10g-1`
- Idle waste: `$20/day` (`$600/month`)
- Audited metrics: GPU utilization, MFU, MBU, and idle hours.

## M2 — Inference Cost Levers

- Baseline: `$48.87/day` (`$6.488/1M-token`)
- Optimized: `$8.48/day` (`$1.126/1M-token`)
- Savings: `82.6%`
- Levers: cascade routing, prompt caching, and batch processing.

## M3 — Purchasing Strategy

- On-demand monthly cost: `$25,667`
- Optimized monthly cost: `$15,627`
- Savings: `39.1%`
- Recommendations included both `spot` and `reserved` tiers.

## M4 — Cost Allocation

- Tag coverage: `92%`
- Chargeback ready: `True`
- FOCUS export: `outputs/focus_export.csv` with 50 rows.

These results were generated from the deterministic lab dataset without modifying the mission source code or tests.
