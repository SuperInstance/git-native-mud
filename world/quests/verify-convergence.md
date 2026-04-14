---
name: verify-convergence
kind: quest
services: [forgemaster, jc1]
---

requires:
- dcs_module: constraint-theory-core/src/dcs.rs compiled
- experiment_scripts: experiments/ directory available
- jetson_access: JC1 online for hardware validation

ensures:
- rigidity_data: phase transition measurements at k=8..16
- ricci_data: convergence timing at multiple swarm sizes
- paper_section: Section 5 experimental results

strategies:
- when GPU available: run 10000 trials for statistical significance
- when edge hardware only: run 100 trials as preliminary validation
- when results contradict theory: document anomaly, don't fake data
