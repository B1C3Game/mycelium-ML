#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python}"
GENERATIONS="${GENERATIONS:-500}"
N_AGENTS="${N_AGENTS:-75}"

SEEDS=(101 102 103 104 105 106 107 108)
RESOURCE_RATIOS=(0.06 0.06 0.08 0.08 0.10 0.10 0.12 0.12)
REGEN_RATIOS=(0.001 0.002 0.001 0.002 0.001 0.002 0.001 0.002)

SWEEP_DIR="outputs/sweeps"
mkdir -p "$SWEEP_DIR"

echo "Starting overnight sweep: runs=${#SEEDS[@]} generations=$GENERATIONS"

for i in "${!SEEDS[@]}"; do
  run_id=$((i + 1))
  seed="${SEEDS[$i]}"
  rr="${RESOURCE_RATIOS[$i]}"
  rg="${REGEN_RATIOS[$i]}"

  run_dir="$SWEEP_DIR/run_${run_id}_seed_${seed}_rr_${rr}_rg_${rg}"
  mkdir -p "$run_dir"

  echo "[Run $run_id/8] seed=$seed resource_ratio=$rr regen_ratio=$rg"
  "$PYTHON_BIN" main.py \
    --generations "$GENERATIONS" \
    --seed "$seed" \
    --resource-ratio "$rr" \
    --resource-regen-ratio "$rg" \
    --n-agents "$N_AGENTS" \
    --output-dir "$run_dir" \
    > "$run_dir/run.log" 2>&1

done

"$PYTHON_BIN" summarize_sweep.py --sweep-dir "$SWEEP_DIR" --expected-generations "$GENERATIONS"

echo "Sweep complete. Decision table: $SWEEP_DIR/decision_table.md"
