#!/usr/bin/env python3
"""Run reconstructed experiments.   python run_all.py --stage all --seeds 3 --procs 2
Stages: sweeps | default | swarm | plots | all.  Results are resumable (results/*.jsonl)."""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dataclasses import asdict
from coopsim import SimConfig
from coopsim import experiments as ex, plots

ap = argparse.ArgumentParser()
ap.add_argument("--stage", default="all")
ap.add_argument("--seeds", type=int, default=3)
ap.add_argument("--default-seeds", type=int, default=5)
ap.add_argument("--procs", type=int, default=2)
ap.add_argument("--sim-time", type=float, default=600.0)
ap.add_argument("--out", default="results")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
base = asdict(SimConfig(sim_time=a.sim_time))
path = os.path.join(a.out, "runs.jsonl")
if a.stage in ("default", "all"):
    ex.run_tasks(ex.default_tasks(range(100, 100 + a.default_seeds), base), path, a.procs)
if a.stage in ("swarm", "all"):
    ex.run_tasks(ex.swarm_tasks(range(100, 102), base), path, a.procs)
if a.stage in ("sweeps", "all"):
    ex.run_tasks(ex.sweep_tasks(range(200, 200 + a.seeds), base), path, a.procs)
if a.stage in ("plots", "all"):
    plots.make_all(ex.load(path), os.path.join(a.out, "figures"))
    print("figures/tables written to", os.path.join(a.out, "figures"))
