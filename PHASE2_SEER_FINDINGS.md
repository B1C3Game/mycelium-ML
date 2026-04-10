# PHASE2_SEER_FINDINGS.md

## Summary: SEER Proof and Phase 2 Evolution

**This document records the key findings, commands, and reproducibility details for the SEER proof and Phase 2 mini sweep.**

---

## Key Findings

1. **Phase 1 proved stability:**
   - System is robust, no crashes, no NaN, population persists for 500+ generations.
2. **Phase 2 proved evolution is active:**
   - Births, mutation, selection, and measurable trait drift/variance are all present.
3. **Phase 2 mini sweep proved robustness under evolution:**
   - 8/8 runs completed, no NaN, no crashes, population survives and adapts across all tested parameters.

**This is a complete POC arc. The system is ready for publication as a research note.**

---

## Commands Used

### Phase 2 Mini Sweep
```
cd ~/0/mycelium-ML.md
mkdir -p outputs/phase2_mini_sweep
for seed in 42 123 456 789; do
  for rr in 0.08 0.12; do
    out="outputs/phase2_mini_sweep/seed_${seed}_rr_${rr}"
    echo "Running seed=$seed rr=$rr -> $out"
    venv/bin/python main.py --seed "$seed" --resource-ratio "$rr" --generations 500 --output "$out"
  done
done
```

### Commit Hash
```
0e2974ee50047d69df3540e7eeb342090d6bb5ea
```

### Output Directory
```
outputs/phase2_mini_sweep/
```

---

## Next Steps

- **Option A (Recommended):**
  - Run a single long simulation (seed 42, rr 0.10, 1000 gens)
  - Generate plots: trait variance and mean over time
  - This will be the centerpiece for the blog/research note
- **Option B:**
  - Expand sweep grid for stress testing
  - Compare Phase 1 vs Phase 2 survival
- **Option C:**
  - Minimal inheritance/spore experiment

---

*Documented by GitHub Copilot, 2026-04-10*