# SAT-Helper

Pedagogical yet surprisingly fast SAT toolkit  
*(pure Python 3 – no third-party packages required)*

| File | Purpose |
|------|---------|
| **`sat_solver_fast.py`** | Stand-alone solver with four engines: Resolution, Davis–Putnam, iterative DPLL, and CDCL (watched-literal + 1-UIP). |
| **`make_benchmarks.py`** | Builds a `bench/` folder, auto-creates five random 3-SAT files (100 – 600 vars), runs **all four** engines on every file in that folder (including any `.cnf` / `.csv` you add), and writes `bench/results.txt`. |
| **`bench/`** | Generated on demand – holds the generated `test*.csv`, any industrial CNFs you drop in, and the benchmark summary. |

---

## Quick install

```bash
git clone https://github.com/GheorgheLuca1/SAT-Helper.git
cd SAT-Helper
python --version     # 3.8 or newer
```

> No `pip install …` needed – everything is standard-library.

---

## 1 · Detailed guide: `sat_solver_fast.py`

### 1.1 Create `clauses.csv`

The solver defaults to **`clauses.csv`** in the current folder.  
Each line is **one clause**, integers separated by spaces, **terminated with `0`** (DIMACS).

Example for  
\`(x₁ ∨ ¬x₂) ∧ (¬x₁ ∨ x₃) ∧ (x₄)\`

```text
1 -2 0
-1  3 0
4 0
```

Save as `clauses.csv`.

### 1.2 Run interactively

```bash
python sat_solver_fast.py          # reads clauses.csv
```

```
Select solver:
1. Resolution
2. Davis–Putnam
3. DPLL (iterative)
4. CDCL (watched + 1-UIP)
Your choice [1-4]:
```

Pick a number – the program prints **SAT / UNSAT / TIME**, wall-clock
runtime, and peak memory.

### 1.3 Alternate input modes

Run a different file:

```bash
python sat_solver_fast.py --file my_formula.cnf
```

Paste clauses manually:

```bash
python sat_solver_fast.py --manual
# type/paste each clause, end with 0
# press Enter on an empty line to finish
```

### 1.4 Non-interactive (scriptable) runs

```bash
echo 4 | python sat_solver_fast.py --file hard.cnf > out.txt
```

*(uses solver 4 = CDCL, avoids the menu – handy for batch scripts)*

---

## 2 · Detailed guide: `make_benchmarks.py`

### 2.1 Generate & run the full benchmark suite

```bash
python make_benchmarks.py
```

This will:

1. Create **`bench/`** (if missing).  
2. Generate five random 3-SAT files:

```
bench/test1.csv   (100 vars)
bench/test2.csv   (200 vars)
…
bench/test5.csv   (600 vars)
```

3. Keep any `.cnf` / `.csv` you already placed in `bench/`.  
4. Solve every file with **Resolution, DP, DPLL, CDCL**  
   (10-second timeout per (file, solver)).  
5. Write **`bench/results.txt`**:

```text
file               vars solver      res   time
--------------------------------------------------
test1.csv           100 Resolution  SAT   0.006s
test1.csv           100 DP          SAT   0.011s
test1.csv           100 DPLL        SAT   0.029s
test1.csv           100 CDCL        SAT   0.003s
...
```

`res` = `SAT`, `UNSAT`, or `TIME` (timeout at 10 s).

### 2.2 Customising

Open **`make_benchmarks.py`** and edit the constants at the top:

```python
RANDOM_SIZES = [50, 100, 150, 200]   # variable counts for test files
ALPHA        = 4.3                   # clause density (m = α·n)
TIMEOUT      = 20                    # seconds per (file, solver)
```

Add industrial problems by copying DIMACS `.cnf` (or space-separated
`.csv`) into `bench/` before running – they will be included automatically.

---

## 3 · Re-generating LaTeX tables / plots

1. Run `make_benchmarks.py`.  
2. Use **`bench/results.txt`** to fill tables in your paper.  
3. For plots, either:

   * open the TXT in Excel / LibreOffice Calc, or  
   * include with PGFPlots:

     ```latex
     \pgfplotstabletypeset[
       columns={solver,time},
       col sep=space
     ]{bench/results.txt}
     ```

*(If you install Matplotlib, the optional `run_benchmarks.py` script can
output ready-made PDF plots.)*

---
