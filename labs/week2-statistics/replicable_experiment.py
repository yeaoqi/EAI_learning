import argparse
import json
import platform
import subprocess
from pathlib import Path

import numpy as np

def git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=float, default=0.7)
    parser.add_argument("--n", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--out",
        type=str,
        default=str(Path(__file__).resolve().parent / "experiment-result.json"),
    )
    args = parser.parse_args()

    if not 0 <= args.p <= 1:
        raise ValueError("p must be in [0, 1]")
    if args.n <= 0:
        raise ValueError("n must be positive")

    rng = np.random.default_rng(args.seed)
    success_rate = float((rng.random(args.n) < args.p).mean())

    result = {
        "config": vars(args),
        "result": {"success_rate": success_rate},
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "git_commit": git_commit(),
        },
    }

    Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
