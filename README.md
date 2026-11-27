# coopsim — independent reconstruction of the token-controlled cooperative routing method (PSO + EGT)

**This is NOT the authors' code.** It was written from the manuscript text only. See `REPORT.md` for what was extracted,
what was assumed, which baselines are surrogates, and the results.

## Layout
```
coopsim/
  config.py       all parameters, each tagged [PAPER]/[ASSUME]/[SCALE]
  utils.py        min-max (Eq.7), clip (Eq.6), sigmoid
  mobility.py     Random Waypoint
  egt.py          Eqs.1-7: payoff, PD matrix, cooperation init, replicator dynamics, roulette population
  trust.py        Eqs.13-14: trust ageing, majority vote
  pso.py          Eqs.8-12: batched discrete PSO (sigmoid/top-K mapping, clamp repair)
  tokens.py       Eqs.15-16: token allocation / remaining tokens
  metrics.py      Eqs.20-24
  simulator.py    encounter-based engine (contacts, hop beacons Eq.18, buffers, TTL, energy)
  protocols.py    Proposed (+ablations PSO-Rand / EGT-Only / No-Token), Epidemic, Spray&Wait, IPSO & QL surrogates
  experiments.py  resumable sweeps / ablation / swarm sensitivity (JSONL)
  plots.py        figures + markdown tables
run_all.py        CLI driver
tests/            unit tests (python tests/test_components.py)
results/          runs.jsonl, run.log, figures/ (PNG, CSV, markdown tables)
```

## Run
```bash
pip install numpy scipy matplotlib
python tests/test_components.py                    # unit tests
python run_all.py --stage all --seeds 3 --procs 2  # ~35 min on 2 cores; resumable
python run_all.py --stage plots                    # re-draw figures from results/runs.jsonl
```
Single run:
```python
from coopsim import SimConfig, Simulator, REGISTRY
cfg = SimConfig(n_nodes=300, sim_time=600, ttl=150)
print(Simulator(cfg, REGISTRY["Proposed"](), seed=1).run())
```
Protocol names: `Proposed`, `Proposed+fallback` (set `cfg.progress_fallback=True`), `PSO-Rand`, `EGT-Only`, `No-Token`,
`Epidemic`, `SprayAndWait`, `IPSO(surrogate)`, `QL(surrogate)`. Use `cfg.token_mode="global"` for the literal Eq.15/16 reading.

Reduced scale vs. the paper (600 s, dt = 1 s, 0.01 pkt/s/node, 3-5 seeds instead of 30 runs) — see REPORT.md §7.
