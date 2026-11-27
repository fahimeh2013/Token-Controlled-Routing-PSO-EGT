# Reconstruction report — "Adaptive Cooperative Packet Replication for Reliable Routing in Multi-Hop Wireless Networks"

> **Status of the code.** Everything in `coopsim/` is an **independent reconstruction written from the manuscript text**.
> It is **not** the authors' source code, and it has not been validated against it.
> Tags used below: **[EXTRACTED]** = stated in the PDF · **[ASSUMED]** = needed for implementation but not stated · **[SURROGATE]** = stand-in for a baseline the paper does not specify well enough to reproduce.

---

## 1. Official source code / supplementary files (task 4)

* The PDF contains **no repository URL, DOI, GitHub/Zenodo/Code-Ocean link or code-availability statement.**
* The *Data Availability* section (p. 37-38) says that data, a "complete algorithmic description (Algorithm 1)", "exact parameter settings (Table 6 and Section S2)", "raw simulation data (Tables S1-S6)" and "reproduction instructions (Section S4)" are in a *Supplementary Information file on the journal's page*. **That supplement is not part of the uploaded PDF**, so I could not inspect it. Code is not listed among its contents; "additional implementation details" are available "from the corresponding author upon reasonable request".
* A web search for the exact title returned no repository or published version (only unrelated papers).
* **Conclusion:** no official implementation could be identified → the code was reconstructed (tasks 5-9).
  If you obtain the journal supplement (Tables S1-S6 / Section S2/S4), several of the assumptions in §6 could be replaced by the authors' real values.

## 2. The proposed routing algorithm [EXTRACTED]

A **destination-oriented, token-controlled, bounded multi-copy** routing scheme for intermittently connected multi-hop networks, with four phases (p. 8):

1. **EGT initialisation.** For each destination *d*, every node plays a binary-strategy (cooperate/defect) evolutionary game; payoff Eq.1, Prisoner's-Dilemma matrix Eq.2, cooperation percentage C<sub>i</sub> (Eqs.4-6). The **roulette-wheel** rule p<sub>i</sub> = C<sub>i</sub>/ΣC<sub>j</sub> builds the PSO initial population (K distinct nodes per particle).
2. **PSO.** Select the subset of K = ⌈0.3 N⌉ "destination-oriented cooperative nodes" maximising the fitness (Eqs.8/9) with velocity/position updates (Eqs.11-12).
3. **Token budget.** Packet gets T<sub>total</sub> ∈ {3, 5, 10} tokens by priority (40 % / 40 % / 20 %).
4. **Routing (Algorithm 1).** When a carrier meets (a) the destination → deliver; (b) a cooperative node for *d* → send one copy plus T<sub>send</sub> tokens (Eq.15), update T<sub>remaining</sub> (Eq.16); (c) otherwise keep carrying. After delivery, cooperation percentages are updated by Q = h(P<sub>s</sub>,T<sub>d</sub>,R) (Eq.19). Hop distances come from 10-s beacons (Eq.18); trust from Eqs.13-14.

## 3. Optimisation problem [EXTRACTED unless noted]

| Item | Content |
|---|---|
| Optimiser | Particle Swarm Optimisation, swarm 50, ≤100 iterations, stop if <0.01 % gain over 10 iterations, w = 0.729, c₁ = c₂ = 2.0, r₁,r₂ ~ U[0,1] |
| Decision variable | per destination *d*: a subset X ⊂ {1..N}, |X| = K = ⌈0.3N⌉; position x<sub>i</sub> ∈ [0,1]<sup>N</sup> (probability vector), selection = top-K of sigmoid(x) |
| Objective (maximise) | F = w₁·P<sub>Co</sub> + w₂(1−E<sub>c,norm</sub>) + w₃(1−T<sub>norm</sub>) + w₄(1−H<sub>c,norm</sub>), w = (0.4, 0.2, 0.2, 0.2) (Eq.9; Eq.8 is the un-normalised 1/x form) |
| Constraints | exactly K distinct nodes; positions clamped to [0,1]; destination cannot be its own cooperator [ASSUMED]; token budget Σcopies ≤ T<sub>total</sub> |
| EGT stage | maximise Σ U<sub>i</sub> (Eq.3); replicator dynamics Eq.5, 50 rounds |

## 4. Equations extracted (numbering as printed in the PDF)

| Eq. | Formula | Implemented in |
|---|---|---|
| 1 | U<sub>i</sub> = α·E<sub>i</sub> + β·R<sub>i</sub> − γ·D<sub>i</sub>, α,β,γ = 0.4,0.3,0.3 | `egt.payoff_utility` |
| 2 | P.M = [[R,S],[T,P]], R = αE<sup>n</sup>+βT<sub>ij</sub>+γ(1−D<sup>n</sup>), T=1.2R, S=0.3R, P=0.5R (T>R>P>S) | `egt.pd_payoff_matrix` (unit-tested; not wired into Eq.5, see §5) |
| 3 | Objective = max Σ U<sub>i</sub> | implicit |
| 4 | C<sub>i</sub> = g(U<sub>i</sub>), g → [0,1] | `egt.initial_cooperation` (min-max) |
| 5 | C<sub>i</sub>(t+1) = C<sub>i</sub>(t) + η[F<sub>i</sub>(t) − F̄(t)] | `egt.replicator_step` |
| 6 | clip(·,0,1) | `utils.clip01` |
| 7 | min-max normalisation | `utils.minmax` |
| 8 / 9 | fitness (1/x form / (1−norm) form) | `pso.node_scores` (Eq.9 form) |
| 10 | S<sub>co,ij</sub> = αT<sub>ij</sub> + βCo<sub>ij</sub> + γHI<sub>ij</sub> (scoring) | **not used** — no quantity in the paper consumes it (see §5) |
| 11, 12 | v(t+1)=w v + c₁r₁(p−x) + c₂r₂(g−x); x(t+1)=x+v | `pso.pso_select` |
| 13 | T<sub>ij</sub>(0)=0.5; T(t+1)=λT(t)+(1−λ)T<sup>new</sup>, λ=0.9 | `trust.age_update` |
| 14 | majority voting, >60 % neighbours approve | `trust.majority_vote` (tested; not exercised, no false reporters simulated) |
| 15 | T<sub>send,i,j</sub> = ⌊T<sub>total,k</sub>·C<sub>j</sub>max(H<sub>iD</sub>−H<sub>jD</sub>,0)/Σ<sub>x∈𝒞</sub>C<sub>x</sub>max(H<sub>iD</sub>−H<sub>xD</sub>,0)⌋ | `tokens.allocate_tokens` |
| 16 | T<sub>remaining</sub> = T<sub>total,k</sub> − Σ<sub>j</sub>T<sub>send,i,j</sub> | `tokens.remaining_tokens` |
| 18 | H<sub>j,D</sub> = min(H<sub>j,D</sub>, H<sub>k,D</sub>+1) per beacon | `Simulator._beacon` |
| 19 | Q = h(P<sub>s</sub>,T<sub>d</sub>,R) | `CoopRouting.on_delivery` (h **assumed**) |
| 20 | Delivery ratio = ΣD<sub>j</sub>/ΣS<sub>j</sub> | `metrics.delivery_ratio` |
| 21 | Average delay = ΣT<sub>j</sub>/ΣD<sub>j</sub> | `metrics.average_delay` |
| 22 | Overhead = Σ(F<sub>j</sub>−D<sub>j</sub>)/ΣD<sub>j</sub> | `metrics.overhead` |
| 23 | Reliability = 1 − Π(1 − C<sub>i</sub>p<sub>i</sub>)<sup>R<sub>i</sub></sup> | `metrics.reliability_analytic` |
| 24 (text calls it 25) | E[hops] = ΣH<sub>iD</sub>P<sub>i</sub><sup>*</sup>, P<sup>*</sup>=1−(1−P<sub>i</sub>)<sup>C<sub>i</sub></sup> | `metrics.expected_hop_count` |

**Pseudocode (Algorithm 1)** is implemented 1:1 in `CoopRouting.refresh` (lines 2-13) and `CoopRouting.forward` / `Simulator.run` (lines 14-28).

## 5. Simulation parameters [EXTRACTED]

1000×1000 m²; N = 100-500 (default 300); Bluetooth/BLE, range 50 m, 1 Mb/s; RWP 1-10 m/s, pause 0-20 s (Gauss-Markov α=0.85 for the heterogeneous case); update step 0.1 s; sim time 1000 s (Table 5) / 500-2000 s (text); 512 B packets; **1 packet/s/node**; buffer 20 (sweep 5-30); lifetime sweep 50-250 s; initial energy 150 J; cooperation threshold 0.7; PSO 50×100; EGT 50 rounds; "Max Token Copies 5"; MATLAB R2022a; 30 independent runs, paired t-tests; baselines IPSO [7], H-PSO-EGT [20], EADQR-QL [48], SWO [49].
Q-learning baseline hyper-parameters: α=0.1, γ=0.9, ε=0.1. Heterogeneous tiers: 30 % (150 m, static), 50 % (100 m, slow), 20 % (50 m, fast).

## 6. Ambiguities / inconsistencies found in the manuscript (not "fixed" silently)

1. **Two incompatible PSO encodings**: index-set positions with velocity [1,−1,2] (p. 10) vs. probability vectors in [0,1]<sup>N</sup> with sigmoid + top-K (p. 16). → implemented the second.
2. **c₁ = c₂ = 2.0 together with w = 0.729 "via the constriction factor"**: Clerc–Kennedy's constriction coefficient 0.729 corresponds to c₁=c₂≈1.494. With c=2 the swarm is not in the convergent regime (measured below).
3. **Eq.8 (1/E<sub>c</sub>, 1/T, 1/H<sub>c</sub>) vs Eq.9 ((1−x<sub>norm</sub>))** — different functions; text says Eq.9 is the one used.
4. **Fitness aggregation over a subset is undefined**, and with a weighted sum of per-node terms the objective is *separable*: its exact optimum is simply the top-K nodes by per-node score, so PSO is, in principle, unnecessary (the tests show PSO only approximates that optimum).
5. **Eq.15 / Eq.16 are not local**: they use T<sub>total,k</sub> and a global T<sub>remaining</sub> although a carrier only knows its own tokens; "carrier always retains one token that is not subtracted" is not defined further. The "O(1) forwarding" claim also ignores the sum over candidates.
6. **Eq.18 is monotone non-increasing and has no ageing**, so hop estimates become uninformative under mobility. When a node has no estimate the progress term of Eq.15 is undefined.
7. **Eq.19's h(·) is not defined**, nor how Q changes C; **η (Eq.5) not given**; the cooperation threshold 0.7 has no stated use; Eq.10 (S<sub>co</sub>) feeds nothing; the payoff matrix (Eq.2) is not connected to the replicator step (Eq.5 uses "fitness derived from U<sub>i</sub>").
8. **Token budget**: Table 5 "Max Token Copies = 5" vs priority tokens {3,5,10}; fitness weights "variable/user-defined" in Table 5 vs fixed 0.4/0.2/0.2/0.2 in the text.
9. **Reliability metric**: the paper's own clarification says simulated reliability = fraction of packets delivered — identical to the delivery ratio by definition — yet Fig. 9 differs numerically from Fig. 5.
10. **Internal numeric inconsistencies** (N = 300): delivery ratio 0.955 (Fig.5a) vs 93.5 % (Tables 7/8); overhead 1.6 (Fig.8a) vs 1.8 (Tables); delay 14.0 ms (Fig.6a) vs 112 ms (Tables 6-8); delay unit ms in Fig.6a/c but s in Fig.6b; improvement claims (abstract 10 %/25 %/11 %/35 %) vs Table 8 (+10.6 %, −22.7 %, +10.2 %, −35.7 %).
11. **Plausibility of the connectivity model**: 300 nodes, 50 m range, 1 km² gives a mean degree ≈ 2.4 (π·50²·300/10⁶), i.e. a sparse, mostly partitioned DTN. Delivery ≈ 93-96 % within 50-250 s lifetimes with ≤10 copies is hard to square with this (see results).
12. **Ablation (Table 7)**: "No-Token" has a *higher* delivery ratio/reliability than the proposed method — consistent with replication being the dominant lever.
13. Equation/section cross-references are shifted in several places (e.g. flowchart cites "Equation 11" for tokens; "Section IV.G"; "Eqs. 9–10" for PSO).
14. Tables S1-S6 / H-PSO-EGT and SWO details are not in the PDF; the original protocols cannot be reproduced from it.

## 7. Assumptions made for the implementation [ASSUMED]

| # | Assumption | Where |
|---|---|---|
| A1 | Discrete-time simulation, dt = 1 s (paper 0.1 s); sim time 600 s; packet generation 0.01 pkt/s/node (paper 1 pkt/s/node would give ≈ 3·10⁵ packets/run and permanent buffer overflow with 20-slot buffers); generation stops TTL seconds before the end | `config.py` |
| A2 | Default packet lifetime 150 s (paper gives only the 50-250 s sweep) | `config.py` |
| A3 | Drop-oldest on buffer overflow; no anti-packets (copies of delivered packets keep circulating); transmissions are instantaneous (1 Mb/s × 512 B = 4 ms ≪ dt) and contacts are unlimited in bandwidth | `simulator.py` |
| A4 | Energy model: 0.2 mJ per transmission, 0.1 mJ per reception (paper has none). 150 J is never depleted, so energy only affects the min-max-normalised terms | `config.py` |
| A5 | Per-node quantities for destination *d*: E = normalised residual energy; D = min-max-normalised Euclidean distance; trust T<sub>id</sub> from Eq.13; fitness terms E<sub>c</sub> = normalised consumed energy, T = distance (delay proxy), H<sub>c</sub> = min-max hop estimate H<sub>i,d</sub>; subset fitness = mean over members | `protocols.refresh` |
| A6 | η = 0.02; F<sub>i</sub> := U<sub>i</sub>; first C = g(U) with min-max, later refreshes continue the dynamics from the stored C | `egt.py` |
| A7 | PSO: initial position = indicator of the roulette-drawn subset, initial velocity 0, positions clamped to [0,1], destination column pinned out of selection | `pso.py` |
| A8 | Trust input T<sup>new</sup>: 1 on every contact with *j* and on delivery to *j*; 0 when a copy for *j* expires undelivered | `simulator.py` |
| A9 | Hop table: Eq.18 each 10-s beacon + a two-window ageing (30 s) so estimates can rise again; unknown hop = 20 | `simulator.py` |
| A10 | Candidate set 𝒞 in Eq.15 = cooperative nodes currently in contact without the packet; **local** mode: budget = carrier's tokens − 1 (conserved, carrier keeps one); **global** mode = literal Eq.15/16. A copy is sent only if T<sub>send</sub> ≥ 1. If Σ weights = 0 forwarding halts (paper-literal); `+fallback` variant uses C-only weights (**not in paper**) | `tokens.py`, `protocols.py` |
| A11 | Eq.19: Q = (1 + (1−T<sub>d</sub>/TTL) + R)/3, R = Laplace-smoothed forwarding success of the relay; C ← C + 0.1(Q − C) for relays on the delivery path | `protocols.on_delivery` |
| A12 | Selection (EGT+PSO) refreshed every 300 s for all destinations in one batch | `config.py` |
| A13 | Reliability reported by simulation = delivered fraction (as the paper's clarification states); hop count = intermediate relay nodes of the delivered copy | `simulator.py` |
| A14 | Results from 3 seeds (sweeps) / 5 seeds (default scenario) rather than 30 runs | `run_all.py` |

## 8. What was / was not implemented (tasks 6-8)

| Component | Status |
|---|---|
| Proposed method (EGT, PSO, trust, tokens, hop beacons, delivery feedback) | implemented from the text |
| Ablations: PSO-Rand, EGT-Only, No-Token | implemented as described in the ablation section |
| Epidemic, Spray-and-Wait | standard definitions |
| IPSO [7] | **[SURROGATE]** — PSO with random init + source-oriented attributes, as summarised in the paper |
| EADQR-QL [48] | **[SURROGATE]** — generic ε-greedy Q-learning relay selection with the paper's α,γ,ε; the fuzzy-logic stage is unspecified |
| H-PSO-EGT [20], SWO [49] | **not implemented** — their algorithms are not described in the manuscript (inventing them would violate the "no invented details" rule) |
| Heterogeneous-node experiment, energy-balance/lifetime numbers, malicious nodes | not reproduced (tier energy/speed values and energy model unspecified) |

---

## 9. Results of the reconstructed simulation (task 9)

Scale: N = 100-500 (default 300), 600 s, dt = 1 s, 0.01 pkt/s/node, TTL 150 s, buffer 20. Sweeps: 3 seeds; default scenario / ablation: 5 seeds; swarm sensitivity: 2 seeds. Files are in `results/figures/`:
`fig5_delivery_ratio.png`, `fig6_average_delay.png`, `fig7_hop_count.png`, `fig8_overhead.png`, `fig9_reliability.png` (each with 3 panels: vs. nodes / lifetime / buffer), `fig10_ablation.png`, `figx_pso_convergence.png`, `table6_swarm_size.md`, `table7_ablation.md`, `table8_statistics.md`, `all_runs.csv` (every run). Raw records: `results/runs.jsonl`.

**Default scenario (N = 300, TTL 150 s, buffer 20; mean of 5 seeds)**

| Protocol | Delivery ratio | Avg delay (s) | Overhead (Eq.22) |
|---|---|---|---|
| Proposed (paper-literal, halts without hop progress) | 0.162 | 67.3 | 3.29 |
| Proposed+fallback (C-only weights if no progress; *not in paper*) | 0.313 | 74.0 | 12.1 |
| IPSO (surrogate) | ≈0.33 | ≈75 | ≈12 |
| QL (surrogate) | 0.158 | 55.8 | 133.9 |
| Spray-and-Wait (L = 5) | ≈0.37 | ≈71 | ≈10.7 |
| Epidemic | 0.672 | 24.8 | ≈286 |

**Ablation (Table 7 analogue; N = 300, 5 seeds)**

| Variant | Delivery ratio | Avg delay (s) | Overhead | PSO iterations |
|---|---|---|---|---|
| Proposed | 0.162 ± 0.006 | 67.3 | 3.29 | 90.6 |
| PSO-Rand | 0.155 ± 0.004 | 70.4 | 3.22 | 98.3 |
| EGT-Only | 0.147 ± 0.008 | 68.3 | 3.54 | – |
| No-Token | 0.528 ± 0.007 | 71.4 | 84.6 | 90.7 |

### Findings (what the reconstruction does and does not support)

1. **The paper's headline numbers are not reproduced under its stated parameters.** The paper reports ≈ 93.5 % delivery, ≈ 1.8 overhead and ≈ +10 % over the best baseline at N = 300. In this reconstruction even *Epidemic* only reaches 0.67 (0.83 at N = 500) and the proposed method 0.16 (paper-literal) / 0.31 (with the fallback). With 50 m range in 1 km² the mean degree is ≈ 2.4, and a packet that may be copied only 3-10 times within 50-250 s simply cannot reach 93 % of random destinations. Either unstated details differ (traffic, contact model, lifetime, density, the hop-distance mechanism) or the reported figures come from a setting not captured by the text; this reconstruction cannot tell which.
2. **Paper-literal forwarding is very conservative.** Eq.15 yields zero tokens when no candidate has a smaller hop estimate than the carrier — which is the common case in a sparse network with 10-s beacons — so replication stops. The overhead is the lowest of all protocols (3.3) but so is the delivery ratio. Relaxing this rule (`Proposed+fallback`, outside the paper) doubles delivery but then behaves like Spray-and-Wait/IPSO-surrogate.
3. **Ablation: qualitative ordering partly matches, magnitudes do not.** Proposed > PSO-Rand > EGT-Only in delivery ratio as in the paper, but the gaps (≈ 0.007-0.015) are about 1-2 standard deviations with 5 seeds, not the 5-7 points in Table 7. **No-Token** has by far the highest delivery (0.53) *and* a 25× larger overhead — consistent with the paper's message that uncontrolled replication is costly, and also showing that replication volume, not cooperative-node selection, drives delivery here.
4. **EGT seeding does help the optimiser** (`figx_pso_convergence.png`): the EGT-seeded swarm starts at a mean best fitness ≈ 0.60 vs ≈ 0.53 for random initialisation and ends at ≈ 0.63 vs ≈ 0.57 after 100 iterations. This is the one claim of the paper (faster/better PSO via EGT initialisation) that the reconstruction supports directly. It translates into at most a marginal delivery gain.
5. **PSO behaviour with the stated hyper-parameters**: with w = 0.729 and c₁ = c₂ = 2 the swarm reaches ≈ 88-99 % of the exact optimum (the objective is separable, so the optimum is the top-K by per-node score) and the 0.01 %/10-iteration stopping rule almost never fires (≈ 90 of 100 iterations used).
6. **Swarm-size sensitivity (Table 6 analogue) is flat** (delivery 0.152-0.165 for 20-150 particles; 2 seeds) — the paper's 82 % → 93.5 % rise with swarm size is not reproduced.
7. **Statistics (Table 8 analogue).** With 5 seeds the paired t-tests are significant (p < 10⁻³) but in the *opposite* direction to the paper against the strongest implemented comparators (Epidemic for delivery/delay, Spray-and-Wait for overhead). These comparators are standard protocols, **not** the paper's SWO baseline, so the table is not a like-for-like replication of the paper's Table 8.
8. **Reliability (Fig.9)** equals the delivery ratio by construction (the paper's own definition for simulated reliability), so Fig. 9 repeats Fig. 5. The analytic Eq.23/24 are implemented in `metrics.py` but are not evaluated in the sweeps.
9. Delay in our figures is in **seconds** (paper mixes ms and s). Energy numbers are not comparable with the paper (no energy model is given).

### Limitations / how to read the numbers
* Reduced scale (600 s, dt = 1 s, 0.01 pkt/s/node, 3-5 seeds instead of 30) and 14 assumptions (§7). Conclusions about absolute values are therefore conditional on those choices; the Proposed variant is sensitive to A9/A10 (hop-table ageing, handling of "no progress").
* IPSO / QL are **surrogates**, H-PSO-EGT and SWO are **missing**; no statement here applies to the original baselines.
* A natural next step is to obtain the journal's supplementary material (Tables S1-S6, Sections S2/S4), replace the assumed values in `config.py`, then re-run `python run_all.py`.

## 10. Reproduce
```bash
cd coop_routing_repro
python tests/test_components.py
python run_all.py --stage all --seeds 3 --default-seeds 5 --procs 2   # ≈ 35 min on 2 cores
```
