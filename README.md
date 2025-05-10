# SAT-Helper

Pedagogical yet surprisingly fast SAT toolkit  
*(pure Python 3 — no third-party packages required)*

| File | Purpose |
|------|---------|
| **`sat_solver_fast.py`** | Stand-alone solver with four engines:<br>Resolution, Davis–Putnam, iterative DPLL, and CDCL (watched-literal + 1-UIP). |
| **`make_benchmarks.py`** | Builds a `bench/` folder, auto-generates five random 3-SAT tests (100–600 vars), runs **all four** engines on everything (including any `.cnf` / `.csv` you drop in), and writes `bench/results.txt`. |
| **`bench/`** | Populated on demand — contains test files (`test*.csv`) and the resulting `results.txt`. |

---

## Quick start

```bash
git clone https://github.com/GheorgheLuca1/SAT-Helper.git
cd SAT-Helper
python sat_solver_fast.py          # interactively pick solver & file
