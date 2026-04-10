# mycelium-ML Project Context

Date: 2026-04-10

## Purpose

Build and validate the first training-capable mycelium-ML slice locally, then run longer unattended training on server.

## Active Execution Mode

- Local workstation for fast iteration and debugging.
- Server for overnight training only after local validation gates pass.
- Operational checklist is in `RUNBOOK-tonight-local-to-server.md`.

## Tonight Scope

- One end-to-end training slice.
- Reproducible run command.
- Output artifacts plus sanity metrics.

## Decision Rule

- Green local gate -> push -> server overnight run.
- Red local gate -> keep iterating locally until stable.
