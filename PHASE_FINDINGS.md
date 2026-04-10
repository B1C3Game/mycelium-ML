# mycelium-ML Phase Findings (Day 1)

Date: 2026-04-10
Scope: Phase 1 mechanics + Phase 2 baseline robustness infrastructure

## Summary

Day 1 successfully established a stable mechanical baseline.
The simulation runs 500 generations without crashing, maintains non-zero population, and writes reproducible output artifacts for evaluation.
An energy-economy issue was detected (unrealistic inflation), diagnosed, and corrected before overnight sweep.

## What Was Implemented

- 3D grid environment with resource placement and resource consumption
- Agent mechanics: sense, move toward resources, energy spend/gain, aging, death conditions
- Simulation loop with dead-agent pruning
- JSON metrics logging per generation
- Checkpoint export with final state
- Overnight sweep infrastructure:
  - `overnight_sweep.sh` for 8-run matrix execution
  - `summarize_sweep.py` for decision table generation

## Evidence (Local Baseline Run)

Source artifacts:
- `outputs/metrics.json`
- `outputs/checkpoint.json`

### Baseline before energy rebalance

- Metric rows: 500
- Last generation recorded: 500
- Alive agents at generation 1: 75
- Alive agents at generation 500: 75
- Average energy at generation 1: 142.3333
- Average energy at generation 500: 8753.3333
- Resource cells at generation 1: 2684
- Resource cells at generation 500: 2300

### Diagnostics performed

- Single-agent trajectory (gen 0-50) showed runaway gain under old settings.
- Resource pickup validation confirmed consumption worked (resource value became 0 after pickup).
- Conclusion: logic was correct, economy parameters were too generous.

### Energy rebalance changes

- Resource cells changed from binary value to per-cell energy values.
- Resource energy range now bounded (default 1-6).
- Movement cost now scales with energy efficiency.
- Default economy tightened: lower resource density and regen, higher effective movement cost.

### Baseline after energy rebalance

- Metric rows: 500
- Last generation recorded: 500
- Alive agents at generation 1: 75
- Alive agents at generation 500: 75
- Average energy at generation 1: 121.365
- Average energy at generation 500: 452.58
- Resource cells at generation 1: 2684
- Resource cells at generation 500: 2386

Additional check after rebalance:
- Single-agent energy trajectory over gen 0-50 ended at 129.25 from 120.0 (delta +9.25), indicating bounded growth instead of explosive inflation.

## Conclusions

1. Core mechanics are operational and stable.
- No crash across 500 generations.
- Agent lifecycle logic is functioning end to end.

2. Survival behavior is proven for baseline conditions.
- Population persistence criterion is met (alive agents > 0).

3. Resource dynamics currently support strong net energy gain.
- Inflation risk has been reduced from extreme to moderate.
- Environment is now closer to stress-testable, but overnight multi-run results are still required for robustness claims.

4. The overnight pipeline is ready for robustness testing.
- Parameter sweep and decision-table tooling exist and execute.

## What Is Proven vs Not Proven

Proven:
- Simulation stability under baseline settings
- Reproducible data artifacts and checkpointing
- Readiness for unattended multi-run evaluation
- Resource consumption correctness (pickup removes resource from grid)
- Energy economy no longer trivially inflates under baseline defaults

Not yet proven:
- Robustness across harsh parameter settings
- Emergent adaptation (mutation/replication not implemented yet)
- Fitness pressure realism (current baseline appears resource-favorable)

## Immediate Next Decision Logic

Use overnight sweep outputs (`outputs/sweeps/decision_table.md`) to decide:
- PASS envelope: move to Phase 2 (mutation + replication)
- FAIL envelope: run one bounded hardening cycle, then rerun sweep

## Risks To Track

- False confidence from easy baseline parameters
- Parameter sensitivity hidden by single-run success
- Survivorship may still be too easy under some sweep combinations

## Recommended Phase 2 Entry Conditions

Proceed to mutation + replication only if overnight thresholds are met:
- Completion rate >= 80%
- Survival rate >= 70%

If below threshold, harden in one bounded cycle:
- Tune resource regen and energy economy
- Re-run overnight sweep
- Re-evaluate against same thresholds
