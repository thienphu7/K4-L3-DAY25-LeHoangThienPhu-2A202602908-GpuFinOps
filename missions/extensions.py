"""Your Turn: reasoning budget and carbon-aware scheduling (illustrative models)."""
import csv
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from finops import pricing, sustainability as s
from missions._common import load_csv, catalog_by_type, num
from missions.m2_inference_levers import MODEL_PRICES


def reasoning_budget(rows, cap_fraction=0.10):
    groups = {"reasoning": {"requests": 0, "cost_usd": 0., "energy_wh": 0.},
              "normal": {"requests": 0, "cost_usd": 0., "energy_wh": 0.}}
    candidates = []
    for i, r in enumerate(rows):
        inp, out = int(r["input_tokens"]), int(r["output_tokens"])
        cached, batch = int(r["cached_input_tokens"]), bool(int(r["is_batch"]))
        reasoning = bool(int(r["is_reasoning"]))
        pin, pout = MODEL_PRICES[r["route_tier"]]
        cost = pricing.request_cost(inp, out, pin, pout, cached_in=cached, batch=batch)
        wh = s.wh_per_query(inp + out, is_reasoning=reasoning)
        g = groups["reasoning" if reasoning else "normal"]
        g["requests"] += 1
        g["cost_usd"] += cost
        g["energy_wh"] += wh
        if reasoning:
            small = pricing.request_cost(inp, out, *MODEL_PRICES["small"], cached_in=cached, batch=batch)
            candidates.append((i, cost-small, wh-s.wh_per_query(inp+out)))
    # No confidence scores in dataset: keep first N, reroute remaining requests.
    keep = math.floor(len(rows)*cap_fraction)
    reroute = candidates[keep:]
    total_cost = sum(g["cost_usd"] for g in groups.values())
    total_wh = sum(g["energy_wh"] for g in groups.values())
    return {"groups": groups, "reasoning_traffic_pct": 100*len(candidates)/len(rows),
            "reasoning_cost_pct": 100*groups["reasoning"]["cost_usd"]/total_cost,
            "cap_fraction": cap_fraction, "rerouted_requests": len(reroute),
            "baseline_cost_usd": total_cost, "optimized_cost_usd": total_cost-sum(x[1] for x in reroute),
            "baseline_energy_wh": total_wh, "optimized_energy_wh": total_wh-sum(x[2] for x in reroute),
            "assumption": "Fixed tokens; reroute excess reasoning to small/non-reasoning. Quality not measured; first-N proxy, not confidence-based routing."}


def carbon_schedule(workloads, catalog):
    jobs = []
    for r in workloads:
        if not int(r["interruptible"]):
            continue
        wh = num(catalog[r["gpu_type"]]["watts"])*num(r["num_gpus"])*num(r["hours_per_day"])*num(r["days"])
        jobs.append({"job_id": r["job_id"], "energy_wh": wh})
    energy = sum(j["energy_wh"] for j in jobs)
    regions = [{"region": region, "price_usd_kwh": s.REGION_PRICE_KWH[region],
                "carbon_g_kwh": s.REGION_CARBON[region], "electricity_usd": s.energy_cost_usd(energy, region),
                "carbon_g": s.carbon_g(energy, region)} for region in s.REGION_CARBON]
    clean = min(regions, key=lambda r:r["carbon_g"])
    cheap = min(regions, key=lambda r:r["electricity_usd"])
    baseline = next(r for r in regions if r["region"] == "us-east-1")
    for job in jobs:
        job["baseline_carbon_g"] = s.carbon_g(job["energy_wh"], "us-east-1")
        job["clean_carbon_g"] = s.carbon_g(job["energy_wh"], clean["region"])
    return {"jobs": jobs, "regions": regions, "cleanest": clean["region"], "cheapest": cheap["region"],
            "carbon_saved_g": baseline["carbon_g"]-clean["carbon_g"],
            "electricity_saved_usd": baseline["electricity_usd"]-clean["electricity_usd"],
            "assumption": "Catalog watts at full rated power; same hours in each region. Electricity only, not GPU rental; latency/transfer costs excluded."}


def run(verbose=True):
    result = {"reasoning": reasoning_budget(load_csv("token_usage.csv")),
              "reasoning_cap_5pct": reasoning_budget(load_csv("token_usage.csv"), 0.05),
              "carbon": carbon_schedule(load_csv("workloads.csv"), catalog_by_type())}
    target = ROOT / "outputs" / "extensions_results.json"
    target.write_text(json.dumps(result, indent=2)+"\n")
    lines = ["## Your Turn — kết quả định lượng", "", "### Ngân sách Reasoning", ""]
    r = result["reasoning"]
    lines += [f"Reasoning: {r['reasoning_traffic_pct']:.2f}% traffic, {r['reasoning_cost_pct']:.2f}% chi phí.",
              "", "| Traffic | Requests | USD | Wh |", "|---|---:|---:|---:|"]
    for name, g in r["groups"].items():
        lines.append(f"| {name} | {g['requests']} | {g['cost_usd']:.4f} | {g['energy_wh']:.2f} |")
    lines += ["", f"Cap 10% traffic: chuyển {r['rerouted_requests']} request sang small/non-reasoning. Chi phí ${r['baseline_cost_usd']:.4f} → ${r['optimized_cost_usd']:.4f}; năng lượng {r['baseline_energy_wh']:.2f} → {r['optimized_energy_wh']:.2f} Wh.",
              "Giả định token không đổi, hệ số năng lượng reasoning 80× của lab. Dataset thiếu confidence: giữ N request đầu là proxy; policy thực tế cần confidence và đánh giá chất lượng.",
              "", "### Carbon-aware scheduling", "", "| Region | USD/kWh | gCO2/kWh | Electricity USD | Carbon g |", "|---|---:|---:|---:|---:|"]
    c = result["carbon"]
    for g in c["regions"]:
        lines.append(f"| {g['region']} | {g['price_usd_kwh']} | {g['carbon_g_kwh']} | {g['electricity_usd']:.2f} | {g['carbon_g']:.2f} |")
    sensitivity = result["reasoning_cap_5pct"]
    sensitivity_line = f"Sensitivity cap 5%: chuyển {sensitivity['rerouted_requests']} request; USD {sensitivity['baseline_cost_usd']:.4f} → {sensitivity['optimized_cost_usd']:.4f}, Wh {sensitivity['baseline_energy_wh']:.2f} → {sensitivity['optimized_energy_wh']:.2f}. Cap 10% không có tác động vì traffic hiện tại chỉ 8,38%; không giả định savings khi chưa chạm cap."
    carbon_heading = lines.index("### Carbon-aware scheduling")
    lines[carbon_heading:carbon_heading] = [sensitivity_line, ""]
    lines += ["", f"Sạch nhất: {c['cleanest']}; rẻ điện nhất: {c['cheapest']}. Chuyển job interruptible từ us-east-1 sang vùng sạch nhất giảm {c['carbon_saved_g']:.2f} gCO2e và ${c['electricity_saved_usd']:.2f} tiền điện.",
              "Ước tính dùng rated watts × GPU-hours, không phải điện đo thực tế. Tiền điện không được cộng lại vào savings thuê GPU. Có trade-off latency, transfer và data residency; không có một vùng vừa rẻ nhất vừa sạch nhất trong catalog."]
    (ROOT/"outputs"/"extensions_report.md").write_text("\n".join(lines)+"\n")
    if verbose:
        print("\n".join(lines))
    return result


if __name__ == "__main__":
    run()
