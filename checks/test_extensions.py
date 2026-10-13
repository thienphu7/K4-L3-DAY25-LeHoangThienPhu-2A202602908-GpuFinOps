import pytest
from missions.extensions import reasoning_budget, carbon_schedule
from finops import sustainability as s


def test_reasoning_cap_changes_energy_without_inventing_price_premium():
    row = dict(input_tokens="1000", output_tokens="100", cached_input_tokens="0",
               is_batch="0", is_reasoning="1", route_tier="small")
    result = reasoning_budget([row]*10)
    assert result["rerouted_requests"] == 9
    assert result["optimized_cost_usd"] == pytest.approx(result["baseline_cost_usd"])
    assert result["optimized_energy_wh"] == pytest.approx(.33*(80+9))


def test_carbon_schedule_excludes_non_interruptible_and_separates_objectives():
    job = dict(job_id="train", gpu_type="H100", hours_per_day="2", days="3", num_gpus="2", interruptible="1")
    result = carbon_schedule([job, dict(job, interruptible="0")], {"H100": {"watts": "700"}})
    assert len(result["jobs"]) == 1
    assert result["jobs"][0]["energy_wh"] == 8400
    assert result["cleanest"] == "europe-north1"
    assert result["cheapest"] == "us-east-wa"
    assert result["carbon_saved_g"] == pytest.approx(8.4*(380-30))
