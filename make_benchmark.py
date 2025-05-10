import random, time, csv, os, sys, multiprocessing as mp, pathlib, importlib

SATMOD = importlib.import_module("sat_solver"
                                 "")

# ---------- configuration -----------------------------------------------
RANDOM_SIZES   = [100, 200, 300, 400, 600]
ALPHA          = 4.3
TIMEOUT        = 10          # seconds per solver
BENCH_DIR      = pathlib.Path("bench")
random.seed(42)
# ------------------------------------------------------------------------


def gen_random_3sat(n, alpha=ALPHA):
    m = int(alpha * n)
    out = []
    for _ in range(m):
        vars_ = random.sample(range(1, n + 1), 3)
        clause = tuple(sorted(v if random.randint(0, 1) else -v for v in vars_))
        out.append(clause)
    return out


def write_dimacs(path, clauses):
    with open(path, "w") as f:
        for cl in clauses:
            f.write(" ".join(map(str, cl)) + " 0\n")


def ensure_random_tests():
    BENCH_DIR.mkdir(exist_ok=True)
    for idx, n in enumerate(RANDOM_SIZES, 1):
        f = BENCH_DIR / f"test{idx}.csv"
        if f.exists():
            continue
        print(f"Creating {f.name}  ({n} vars)")
        write_dimacs(f, gen_random_3sat(n))


def load_clauses(path: pathlib.Path):
    clauses = []
    with open(path) as f:
        for ln in f:
            lits = [int(tok) for tok in ln.split() if int(tok) != 0]
            if lits:
                clauses.append(tuple(sorted(lits)))
    return clauses


# ------------ multiprocessing wrapper for time-out -----------------------

def _worker(solver_name, clauses, return_dict):
    t0 = time.perf_counter()
    try:
        if solver_name == "Resolution":
            res = SATMOD.resolution_only(list(clauses))
        elif solver_name == "DP":
            res = SATMOD.dp_loop(list(clauses))
        elif solver_name == "DPLL":
            res = SATMOD.dpll_iterative(list(clauses))
        elif solver_name == "CDCL":
            res = SATMOD.cdcl_solver(list(clauses))
        else:
            res = None
    except Exception:
        res = None
    return_dict["result"] = res
    return_dict["time"]   = time.perf_counter() - t0


def run_with_timeout(solver_name, clauses):
    mgr = mp.Manager()
    ret = mgr.dict()
    p = mp.Process(target=_worker, args=(solver_name, clauses, ret))
    p.start()
    p.join(TIMEOUT)
    if p.is_alive():
        p.terminate()
        p.join()
        return "TIME", TIMEOUT
    res = ret.get("result", None)
    runtime = ret.get("time", TIMEOUT)
    status = "SAT" if res == 1 else "UNSAT" if res == 0 else "TIME"
    return status, runtime


# ------------------- main benchmark loop ---------------------------------

def main():
    ensure_random_tests()

    solvers = ["Resolution", "DP", "DPLL", "CDCL"]
    rows = []

    files = sorted(p for p in BENCH_DIR.iterdir()
                   if p.suffix.lower() in (".csv", ".cnf", ".txt"))
    for path in files:
        clauses = load_clauses(path)
        nvars = max(abs(l) for cl in clauses for l in cl)
        print(f"\n▶ {path.name}  ({nvars} vars, {len(clauses)} clauses)")
        for sol in solvers:
            status, rt = run_with_timeout(sol, clauses)
            print(f"   {sol:<10} {status:<5}  {rt:>6.3f}s")
            rows.append((path.name, nvars, sol, status, f"{rt:.3f}s"))

    # write summary
    out = BENCH_DIR / "results.txt"
    with open(out, "w") as f:
        f.write(f"{'file':<18} {'vars':>5} {'solver':<10} "
                f"{'res':<6} {'time':>8}\n")
        f.write("-" * 50 + "\n")
        for r in rows:
            f.write(f"{r[0]:<18} {r[1]:>5} {r[2]:<10} {r[3]:<6} {r[4]:>8}\n")
    print(f"\nSummary written to {out.resolve()}")


if __name__ == "__main__":
    mp.set_start_method("spawn")
    main()
