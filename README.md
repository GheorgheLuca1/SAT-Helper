# SAT-Helper

Pedagogical yet surprisingly fast SAT toolkit  
*(pure Python 3 – no third-party packages required)*  

| File | Purpose |
|------|---------|
| **`sat_solver_fast.py`** | Stand-alone solver offering four engines: Resolution, Davis–Putnam, iterative DPLL, and CDCL (watched-literal + 1-UIP). |
| **`make_benchmarks.py`** | Generates a `bench/` folder, auto-creates five random 3-SAT tests (100–600 vars), runs **all four** engines on every file in that folder (including any `.cnf` / `.csv` you add), and writes `bench/results.txt`. |
| **`bench/`** | Populated on demand – holds `test*.csv`, any industrial CNFs you drop in, and the result summary. |
