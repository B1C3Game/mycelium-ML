# mycelium-ML

A local-first mycelium simulation where agents sense resources, move toward nutrients, consume energy, and survive across generations in a 3D grid.

## Repository

GitHub: https://github.com/B1C3Game/mycelium-ML

## GitHub Repo Description (Copy Ready)

mycelium-ML is a 3D agent simulation that tests emergent survival dynamics from simple rules, then validates robustness with overnight parameter sweeps.

## What This Repo Proves Right Now

- Agents can sense nearby resources and move toward them.
- Energy mechanics are stable (cost to move, gain on consumption).
- Population can stay alive through a 500-generation run.
- Metrics and checkpoints are written as JSON artifacts.

## Current Scope (Locked)

Included:
- 3D grid with resource placement and regeneration
- Agent sensing and growth mechanics
- Death rules and dead-agent pruning
- Simulation loop and per-generation metrics
- Checkpoint export
- Overnight robustness sweep and decision table generation

Not included (by design for this phase):
- Mutation
- Replication
- Visualization

## Project Files

- main.py: core simulation mechanics and CLI entry point
- overnight_sweep.sh: 8-run overnight matrix launcher
- summarize_sweep.py: builds decision_table.md from sweep outputs
- requirements.txt: Python dependencies
- RUNBOOK-tonight-local-to-server.md: local -> server operating protocol
- PROJECT.md: project execution context
- PHASE_FINDINGS.md: current findings and conclusions from completed phases

## Quick Start (Local Workstation)

### 1) Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

### 2) Run acceptance gates

```bash
python main.py --acceptance-only
```

### 3) Run standard 500-generation simulation

```bash
python main.py --generations 500 --output-dir outputs
```

Outputs:
- outputs/metrics.json
- outputs/checkpoint.json

## Overnight Robustness Sweep

### Run the full sweep

```bash
bash overnight_sweep.sh > overnight_$(date +%Y%m%d_%H%M%S).log 2>&1 &
```

The sweep runs 8 parameter combinations with varying seed and resource settings.

### Output artifacts

- outputs/sweeps/run_*/metrics.json
- outputs/sweeps/run_*/checkpoint.json
- outputs/sweeps/decision_table.md

## Robustness Decision Criteria

- Completion target: >= 80% of runs reach configured generations
- Survival target: >= 70% of runs end with alive_agents > 0

If both pass, continue to next phase.
If either fails, run one bounded hardening cycle and retest.

## Server Handoff (After Local Gate Is Green)

```bash
cd ~/mycelium-ml
git pull origin main
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x overnight_sweep.sh
bash overnight_sweep.sh > overnight_$(date +%Y%m%d_%H%M%S).log 2>&1 &
```

## Goal For Tomorrow

Use decision_table.md to choose one path:
- Robust -> Phase 2 (mutation + replication)
- Fragile -> one bounded hardening cycle, then rerun overnight sweep
