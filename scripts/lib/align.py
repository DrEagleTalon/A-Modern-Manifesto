"""Monotonic sequence alignment (Gale-Church style) with lexical anchors.

Used once, to create the first German/English/modern alignment. Every bead that
is not a clean 1-1 match, or that looks doubtful, is flagged `review: true`
in the verse files so a human checks it.
"""
import math
import re

BEADS = [(1, 1), (1, 0), (0, 1), (2, 1), (1, 2), (2, 2), (3, 1), (1, 3)]
PRIOR = {(1, 1): 0.0, (1, 0): 4.5, (0, 1): 4.5, (2, 1): 2.3, (1, 2): 2.3, (2, 2): 4.0, (3, 1): 4.0, (1, 3): 4.0}

MARKER = re.compile(r"\[\[[A-Z]\d+\]\]")


def strip(s: str) -> str:
    return re.sub(r"\s+", " ", MARKER.sub("", s)).strip()


def _phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def length_cost(la: int, lb: int, ratio: float, var: float = 6.8) -> float:
    if la == 0 and lb == 0:
        return 0.0
    mean = (la + lb / ratio) / 2
    delta = (lb - la * ratio) / math.sqrt(max(mean, 1) * var)
    p = 2 * (1 - _phi(abs(delta)))
    return -math.log(max(p, 1e-12))


NAME = re.compile(r"\b[A-ZÄÖÜ][a-zäöüéèß]{3,}\b")
NUM = re.compile(r"\b\d{2,4}\b")
STOP_CAPS = {"Die", "Der", "Das", "Den", "Dem", "Des", "Ein", "Eine", "Und", "Aber", "Sie", "Wir", "Mit", "Von", "Auch",
             "The", "This", "That", "They", "With", "From", "But", "And", "When", "What", "Their", "There", "These", "Those"}


def anchors(s: str):
    s = strip(s)
    names = {w.lower()[:5] for w in NAME.findall(s) if w not in STOP_CAPS}
    nums = set(NUM.findall(s))
    q = s.count("?")
    return names, nums, q


def anchor_cost(a: str, b: str) -> float:
    na, ma, qa = anchors(a)
    nb, mb, qb = anchors(b)
    cost = 0.0
    cost += 1.5 * len(ma ^ mb)            # numbers are strong anchors
    cost -= 1.0 * len(ma & mb)
    shared = len(na & nb)
    cost -= 0.6 * min(shared, 4)
    cost += 0.8 * abs(qa - qb)
    return cost


def cross_lang_cost(A, B, ratio):
    def f(a_items, b_items):
        a = " ".join(a_items)
        b = " ".join(b_items)
        la, lb = len(strip(a)), len(strip(b))
        c = length_cost(la, lb, ratio)
        if a_items and b_items:
            c += anchor_cost(a, b)
        return c
    return f


_WORD = re.compile(r"[a-z]{4,}")


def _stem(w):
    w = re.sub(r"is(e|ed|es|ing|ation)$", r"iz\1", w)       # -ise/-ize
    w = re.sub(r"our(s|ed|ing)?$", r"or\1", w).replace("ou", "o") if w.endswith(("our", "ours", "oured", "ouring")) else w
    for suf in ("ings", "ing", "ies", "ied", "es", "ed", "s", "ly"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[: -len(suf)]
    return w


def same_lang_cost(ratio=1.0):
    def f(a_items, b_items):
        a = strip(" ".join(a_items)).lower()
        b = strip(" ".join(b_items)).lower()
        la, lb = len(a), len(b)
        c = 0.5 * length_cost(la, lb, ratio, var=12.0)
        if a_items and b_items:
            wa = {_stem(w) for w in _WORD.findall(a)}
            wb = {_stem(w) for w in _WORD.findall(b)}
            if wa and wb:
                sim = len(wa & wb) / math.sqrt(len(wa) * len(wb))
            else:
                sim = 0.0
            # scale by bead size so merging sentences is not artificially cheap
            c += 8.0 * (1 - sim) * max(len(a_items), len(b_items))
        return c
    return f


def align(A, B, cost_fn, beads=BEADS, prior=PRIOR, band=None):
    """Return list of (a_idx_list, b_idx_list, cost). `band` limits the search to
    cells near the diagonal, which keeps whole-text sentence alignment fast."""
    n, m = len(A), len(B)
    INF = float("inf")
    D = [[INF] * (m + 1) for _ in range(n + 1)]
    back = [[None] * (m + 1) for _ in range(n + 1)]
    D[0][0] = 0.0
    for i in range(n + 1):
        for j in range(m + 1):
            if D[i][j] == INF:
                continue
            if band is not None and n and abs(j - i * m / n) > band:
                continue
            for da, db in beads:
                ni, nj = i + da, j + db
                if ni > n or nj > m:
                    continue
                c = D[i][j] + prior[(da, db)] + cost_fn(A[i:ni], B[j:nj])
                if c < D[ni][nj]:
                    D[ni][nj] = c
                    back[ni][nj] = (i, j)
    out = []
    i, j = n, m
    while (i, j) != (0, 0):
        pi, pj = back[i][j]
        c = D[i][j] - D[pi][pj]
        out.append((list(range(pi, i)), list(range(pj, j)), c))
        i, j = pi, pj
    return out[::-1]
