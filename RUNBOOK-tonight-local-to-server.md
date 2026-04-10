# Tonight Execution Runbook (Local -> Server)

Date: 2026-04-10

## Objective

Use workstation speed for rapid iteration tonight, then move stable code to server for unattended overnight training.

## Why This Path

- Local workstation (RTX 5070) gives faster debug loops and iteration speed.
- Server run should only start from a known-good commit.
- This minimizes wasted overnight cycles and failed long runs.

## Phase 1: Local Fast Iteration (Tonight)

### Scope Lock

Ship one end-to-end slice only:
- Parse input
- Run training step
- Save outputs
- Load outputs for quick validation

Out of scope tonight:
- Major refactors
- New architecture
- Nice-to-have UI polish

### Local Gate (Must pass before handoff)

1. Reproducible run command exists.
2. Required dependencies are captured.
3. One short run completes without manual intervention.
4. Output artifacts are written to expected paths.
5. Basic sanity metrics are logged.

If any gate fails, do not push for overnight run.

## Phase 2: GitHub Handoff

### Commit Policy

- Commit only what is needed for overnight training.
- Keep commit message explicit about run intent.

Suggested message:
- feat: stable training slice for overnight server run

### Push Policy

- Push to main only when local gate is green.
- If uncertain, push to a feature branch first and run server test from that branch.

## Phase 3: Server Overnight Run

### Server Bootstrap

1. Clone or pull latest repository state.
2. Create/activate virtual environment.
3. Install pinned dependencies.
4. Verify environment variables and paths.
5. Start training with logging enabled.

### Overnight Command Rules

- Write logs to timestamped files.
- Write checkpoints regularly.
- Do not rely on interactive shell state.
- Use explicit relative or absolute paths.

### Safety Gate

Before leaving overnight run unattended, confirm:
1. Process is alive.
2. Log file is growing.
3. First checkpoint or first metric line is written.

## Morning Review Checklist

1. Did run complete or stop early?
2. Best metric value and epoch/step.
3. Any divergence, NaN, OOM, or data errors.
4. Confirm output artifacts are valid and loadable.
5. Record result in MEMORY.md with next action.

## Decision Rule

- If overnight run is clean and metrics improve, continue on server.
- If overnight run fails or quality is unclear, return to local debug loop with one bounded fix cycle.

## Timebox For Tonight

- 60 to 90 min: implementation and wiring
- 30 min: local gate validation
- 15 min: commit, push, server start
- 10 min: first-health check before leaving

## Definition of Success (Tonight)

- One validated local training slice
- One clean push to GitHub
- One running overnight server job with logs and checkpoints
