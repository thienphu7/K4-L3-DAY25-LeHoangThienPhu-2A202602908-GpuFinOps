"""Run bonuses locally and save evidence. Exporter uses README's no-Docker path."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
from urllib.request import urlopen
from http.server import HTTPServer

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def main():
    env = os.environ.copy()
    env["HF_HOME"] = str(ROOT/".venv"/"huggingface")
    env["TORCH_HOME"] = str(ROOT/".venv"/"torch-cache")
    results = {}
    for name, script in [("tracker", "litellm_tracker/demo.py"), ("local_model", "local_model/run_local.py")]:
        completed = subprocess.run([sys.executable, str(ROOT/"bonus"/script)], env=env,
                                   text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (OUT/f"bonus_{name}.log").write_text(completed.stdout)
        results[name] = {"exit_code": completed.returncode,
                         "completed": completed.returncode == 0 and "[skip]" not in completed.stdout}
        print(completed.stdout, flush=True)
    spec = importlib.util.spec_from_file_location("exporter", ROOT/"bonus/docker/exporter.py")
    exporter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exporter)
    server = HTTPServer(("127.0.0.1", 0), exporter.Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/metrics", timeout=10) as response:
            body = response.read().decode()
            assert response.status == 200
        assert body.count("gpu_mfu{") == 11
        (OUT/"bonus_exporter.prom").write_text(body)
        results["observability"] = {"http_status": 200, "gpus": 11,
                                    "mode": "Python exporter HTTP scrape; Docker/Grafana not run (Docker unavailable)"}
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    (OUT/"bonus_results.json").write_text(json.dumps(results, indent=2)+"\n")
    print(json.dumps(results, indent=2))
    return 0 if all(r["completed"] for r in list(results.values())[:2]) else 1


if __name__ == "__main__":
    sys.exit(main())
