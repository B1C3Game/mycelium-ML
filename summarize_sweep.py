from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List


def _load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def summarize_runs(sweep_dir: Path, expected_generations: int) -> str:
    run_dirs = sorted([p for p in sweep_dir.iterdir() if p.is_dir() and p.name.startswith("run_")])
    if not run_dirs:
        raise RuntimeError(f"No run directories found in {sweep_dir}")

    rows: List[str] = []
    completed_count = 0
    alive_count = 0

    for run_dir in run_dirs:
        checkpoint_path = run_dir / "checkpoint.json"
        metrics_path = run_dir / "metrics.json"

        if not checkpoint_path.exists() or not metrics_path.exists():
            rows.append(f"| {run_dir.name} | missing | missing | missing | FAIL |")
            continue

        checkpoint = _load_json(checkpoint_path)
        metrics = _load_json(metrics_path)

        final_state = checkpoint["final_state"]
        last_generation = int(final_state.get("last_generation", 0))
        alive_agents = int(final_state.get("alive_agents", 0))

        completed = last_generation >= expected_generations
        alive = alive_agents > 0

        if completed:
            completed_count += 1
        if alive:
            alive_count += 1

        run_status = "PASS" if completed and alive else "FAIL"
        rows.append(
            "| "
            + f"{run_dir.name} | {last_generation} | {alive_agents} | {len(metrics)} | {run_status} |"
        )

    total_runs = len(run_dirs)
    completion_rate = completed_count / total_runs
    alive_rate = alive_count / total_runs

    completion_target = 0.80
    alive_target = 0.70

    overall_pass = completion_rate >= completion_target and alive_rate >= alive_target
    overall_status = "PASS" if overall_pass else "FAIL"

    lines = [
        "# Overnight Sweep Decision Table",
        "",
        f"- Total runs: {total_runs}",
        f"- Completion rate: {_pct(completion_rate)} (target: {_pct(completion_target)})",
        f"- Survival rate: {_pct(alive_rate)} (target: {_pct(alive_target)})",
        f"- Overall status: {overall_status}",
        "",
        "| run | last_generation | alive_agents | metric_rows | status |",
        "|---|---:|---:|---:|---|",
    ]
    lines.extend(rows)
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize overnight sweep results")
    parser.add_argument("--sweep-dir", type=str, default="outputs/sweeps")
    parser.add_argument("--expected-generations", type=int, default=500)
    args = parser.parse_args()

    sweep_dir = Path(args.sweep_dir)
    sweep_dir.mkdir(parents=True, exist_ok=True)

    report = summarize_runs(sweep_dir=sweep_dir, expected_generations=args.expected_generations)
    report_path = sweep_dir / "decision_table.md"
    report_path.write_text(report, encoding="utf-8")

    print(f"Decision table written: {report_path}")


if __name__ == "__main__":
    main()
