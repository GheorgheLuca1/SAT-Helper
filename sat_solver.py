import sys, time, tracemalloc, random, argparse
from itertools import combinations

DEBUG = False

# ------------------------------- CNF helpers -------------------------------

EMPTY = tuple()


def clause_sat(cl, asn):
    return any(((lit > 0) == asn.get(abs(lit), (lit > 0))) for lit in cl)


def clause_conflict(cl, asn):
    return all(abs(lit) in asn and ((lit > 0) != asn[abs(lit)]) for lit in cl)


# --------------------------- 1. Resolution ---------------------------------

def resolve(c1, c2):
    for lit in c1:
        if -lit in c2:
            return tuple(sorted({*c1, *c2} - {lit, -lit}))
    return None


def resolution_only(clauses):
    clauses = list(clauses)
    while True:
        new_clause = None
        for c1, c2 in combinations(clauses, 2):
            res = resolve(c1, c2)
            if res is not None and res not in clauses:
                if DEBUG:
                    print(f"New clause {res} from {c1}+{c2}")
                if res == EMPTY:
                    print("Derived empty clause ⇒ UNSATISFIABLE")
                    return 0
                new_clause = res
                break
        if new_clause is None:
            print("No new clauses ⇒ SATISFIABLE")
            return 1
        clauses.append(new_clause)


# --------------------------- 2. Davis–Putnam -------------------------------

def unit_literal(clauses):
    return next((cl[0] for cl in clauses if len(cl) == 1), None)


def pure_literal(clause_list):
    lits = {lit for cl in clause_list for lit in cl}
    for lit in lits:
        if -lit not in lits:
            return lit
    return None


def dp_loop(clauses):
    clauses = list(clauses)
    while EMPTY not in clauses and clauses:
        # 1-literal
        while (lit := unit_literal(clauses)) is not None:
            clauses = propagate(lit, clauses)
            if clauses is None:
                clauses = [EMPTY]
                break
        if EMPTY in clauses or not clauses:
            break
        while (lit := pure_literal(clauses)) is not None:
            clauses = [cl for cl in clauses if lit not in cl]
        if not clauses or EMPTY in clauses:
            break
        # one resolution step
        new = resolve(clauses[0], clauses[1])
        if new is not None and new not in clauses:
            clauses.append(new)
            if DEBUG:
                print(f"DP added {new}")
    print("UNSATISFIABLE" if EMPTY in clauses else "SATISFIABLE")


# ------------------------- 3. Iterative DPLL -------------------------------

def propagate(lit, clauses):
    new = []
    for cl in clauses:
        if lit in cl:
            continue
        if -lit in cl:
            cl = tuple(l for l in cl if l != -lit)
            if not cl:
                return None
        new.append(cl)
    return new


def dpll_iterative(clauses):
    stack = [(clauses, {})]
    while stack:
        formula, asn = stack.pop()
        changed = True
        while changed:
            changed = False
            # unit
            while (lit := unit_literal(formula)) is not None:
                asn[abs(lit)] = lit > 0
                formula = propagate(lit, formula)
                if formula is None:
                    break
                changed = True
            if formula is None:
                break
            lit = pure_literal(formula)
            if lit is not None:
                asn[abs(lit)] = lit > 0
                formula = [cl for cl in formula if lit not in cl]
                changed = True
        if formula is None:
            continue
        if not formula:
            return True
        lit = formula[0][0]
        stack.append((propagate(-lit, formula), {**asn, abs(lit): lit < 0}))
        stack.append((propagate(lit, formula),  {**asn, abs(lit): lit > 0}))
    return False


# --------------------- 4. CDCL (watched, 1-UIP) ----------------------------

class Assign:
    def __init__(self):
        self.map = {}
        self.trail = []

    def val(self, lit):
        if abs(lit) not in self.map:
            return None
        v, *_ = self.map[abs(lit)]
        return v if lit > 0 else not v

    def set(self, var, val, lvl, ante):
        self.map[var] = (val, lvl, ante)
        self.trail.append(var)

    def backjump(self, lvl):
        while self.trail and self.map[self.trail[-1]][1] > lvl:
            var = self.trail.pop()
            del self.map[var]


def cdcl_solver(clauses):
    num_vars = max(abs(l) for cl in clauses for l in cl)
    watch = {lit: [] for lit in range(-num_vars, num_vars + 1) if lit}
    def watch_clause(cl):
        if len(cl) == 1:
            watch[cl[0]].append(cl)
        else:
            watch[cl[0]].append(cl); watch[cl[1]].append(cl)

    for c in clauses:
        watch_clause(c)

    assign = Assign()
    lvl, conflicts, next_restart = 0, 0, 64
    learnt = []

    def bcp():
        queue = [lit for var in assign.trail[-1:]
                 for lit in (assign.map[var][0] and var or -var,)]
        while queue:
            lit_false = -queue.pop()
            wl = watch[lit_false][:]
            for cl in wl:
                if lit_false not in cl: continue
                for other in cl:
                    if other != lit_false and assign.val(other) is not False:
                        watch[lit_false].remove(cl)
                        watch[other].append(cl)
                        break
                else:
                    unassigned = [l for l in cl if assign.val(l) is None]
                    if not unassigned:
                        return cl
                    if len(unassigned) == 1:
                        u = unassigned[0]
                        assign.set(abs(u), u > 0, lvl, cl)
                        queue.append(u)
        return None

    while True:
        confl = bcp()
        if confl:
            conflicts += 1
            if lvl == 0:
                print("UNSATISFIABLE")
                return 0
            learnt_clause = list(confl)
            seen, counter = set(), 0
            while True:
                var = assign.trail.pop()
                val, lv, ante = assign.map[var]
                seen.add(var)
                if ante and var in [abs(l) for l in learnt_clause]:
                    learnt_clause = list(set(learnt_clause + list(ante)))
                if lv == lvl:
                    counter += 1
                if counter == 1:
                    break
            back_lvl = max([0] + [assign.map[abs(l)][1]
                                   for l in learnt_clause if abs(l) in assign.map
                                   and assign.map[abs(l)][1] != lvl])
            assign.backjump(back_lvl)
            lvl = back_lvl
            learnt_clause = tuple(sorted(set(learnt_clause)))
            learnt.append(learnt_clause)
            watch_clause(learnt_clause)
            continue
        if len(assign.map) == num_vars:
            print("SATISFIABLE")
            return 1
        if conflicts >= next_restart:
            assign.backjump(0)
            lvl = 0
            next_restart *= 2
        lvl += 1
        for v in range(1, num_vars + 1):
            if v not in assign.map:
                assign.set(v, True, lvl, None)
                break




def load_from_file(path):
    data = []
    with open(path, encoding='utf-8') as f:
        for ln in f:
            lits = [int(tok) for tok in ln.split() if int(tok) != 0]
            data.append(tuple(sorted(lits)))
    return data


def load_manual():
    print("Enter CNF clauses (integers, end each line with 0). Blank line to finish.")
    clauses = []
    while True:
        ln = sys.stdin.readline()
        if ln.strip() == "":
            break
        lits = [int(tok) for tok in ln.split() if int(tok) != 0]
        clauses.append(tuple(sorted(lits)))
    return clauses


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="clauses.csv",
                    help="DIMACS-style clause file (default clauses.csv)")
    ap.add_argument("--manual", action="store_true",
                    help="read clauses from stdin instead of file")
    args = ap.parse_args()

    clauses = load_manual() if args.manual else load_from_file(args.file)
    if not clauses:
        print("No clauses loaded — exiting.")
        return

    print("\nLoaded clause set:")
    for cl in clauses:
        print(cl)

    print("\nSelect solver:")
    print("1. Resolution")
    print("2. Davis–Putnam")
    print("3. DPLL (iterative)")
    print("4. CDCL (watched + 1-UIP)")
    try:
        choice = int(input("Your choice [1-4]: "))
    except ValueError:
        print("Bad input. Abort."); return

    tracemalloc.start(); t0 = time.perf_counter()

    if choice == 1:
        resolution_only(list(clauses))
    elif choice == 2:
        dp_loop(list(clauses))
    elif choice == 3:
        sat = dpll_iterative(list(clauses))
        print("SATISFIABLE" if sat else "UNSATISFIABLE")
    elif choice == 4:
        cdcl_solver(list(clauses))
    else:
        print("Unknown option."); return

    cur, peak = tracemalloc.get_traced_memory()
    print(f"\nTime: {time.perf_counter() - t0:.4f} s  |  "
          f"Peak mem: {peak/1024:.1f} KB")

if __name__ == "__main__":
    main()
