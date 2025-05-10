# SAT-Helper

Pedagogical yet surprisingly fast SAT toolkit  
(pure Python 3 – no third-party packages required)

| File                 | Purpose                                                                                                     |
|----------------------|-------------------------------------------------------------------------------------------------------------|
| **sat_solver_fast.py** | Stand-alone solver offering four engines: Resolution, Davis–Putnam, iterative DPLL, and CDCL (watched-literal + 1-UIP). |
| **make_benchmarks.py** | Generates a `bench/` folder, auto-creates five random 3-SAT tests (100–600 vars), runs **all four** engines on every file in that folder (including any `.cnf` / `.csv` you add), and writes `bench/results.txt`. |
| **bench/**            | Populated on demand – holds `test*.csv`, any industrial CNFs you drop in, and the result summary.          |

---


1 · Detailed guide: sat_solver_fast.py
1.1 Create clauses.csv
The solver defaults to a file named clauses.csv in the same folder.
Each line is one clause, integers separated by spaces, and ends with 0 (classic DIMACS).

Example for
(x₁ ∨ ¬x₂) ∧ (¬x₁ ∨ x₃) ∧ (x₄)

diff
Copy
Edit
1 -2 0
-1 3 0
4 0
Save that as clauses.csv.

1.2 Run interactively
bash
Copy
Edit
python sat_solver_fast.py            # uses clauses.csv
You’ll see:

markdown
Copy
Edit
Select solver:
1. Resolution
2. Davis–Putnam
3. DPLL (iterative)
4. CDCL (watched + 1-UIP)
Your choice [1-4]:
Pick a number – the program prints SAT / UNSAT / TIME, wall-clock runtime, and peak memory.

1.3 Alternate input modes
Point to a different file

bash
Copy
Edit
python sat_solver_fast.py --file my_formula.cnf
Paste clauses manually

bash
Copy
Edit
python sat_solver_fast.py --manual
# type or paste each clause, end with 0
# press Enter on a blank line to finish
1.4 Non-interactive (scriptable) runs
Pass the solver number via echo / pipe:

bash
Copy
Edit
echo 4 | python sat_solver_fast.py --file hard.cnf > out.txt
Useful for batch automation.

2 · Detailed guide: make_benchmarks.py
2.1 Generate & run full benchmark suite
bash
Copy
Edit
python make_benchmarks.py
What happens:

A directory bench/ is created (if absent).

Five random 3-SAT files appear:

bash
Copy
Edit
bench/test1.csv   (100 vars)
bench/test2.csv   (200 vars)
…
bench/test5.csv   (600 vars)
Any .cnf / .csv you already placed in bench/ are kept.

Each file is run with Resolution, DP, DPLL, CDCL (10-second timeout per solver).

Results land in bench/results.txt:

markdown
Copy
Edit
file               vars solver      res   time
--------------------------------------------------
test1.csv           100 Resolution  SAT   0.006s
test1.csv           100 DP          SAT   0.011s
test1.csv           100 DPLL        SAT   0.029s
test1.csv           100 CDCL        SAT   0.003s
...
res = SAT, UNSAT, or TIME (timeout at 10 s).

2.2 Customising
Edit the constants at the top of make_benchmarks.py:

python
Copy
Edit
RANDOM_SIZES = [50, 100, 150, 200]   # variable counts for test files
ALPHA        = 4.3                   # clause density (m = α·n)
TIMEOUT      = 20                    # seconds per (file, solver)
Add industrial problems by copying them (DIMACS .cnf or space-separated .csv) into bench/ before running.

3 · Re-generating the paper’s tables / plots
Run make_benchmarks.py.

Use bench/results.txt to populate the LaTeX tables.

For plots, open the TXT in Excel / LibreOffice or include via PGFPlots:

latex
Copy
Edit
\pgfplotstabletypeset[
   columns={solver,time},
   col sep=space
]{bench/results.txt}
(If you install Matplotlib, the optional run_benchmarks.py script can generate PDF plots automatically.)
