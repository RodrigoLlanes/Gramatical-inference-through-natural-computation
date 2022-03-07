from grammar import Grammar
from itertools import product
from typing import Set, Dict, Tuple, List, Optional, Iterator

Symbol = str
Word = List[Symbol]


def cyk_table(g: Grammar, w: Word) -> Dict[Tuple[int, int], Set[Symbol]]:
    n = len(w)
    v = dict()

    for i in range(1, n+1):
        v[i, 1] = {a for (a, bc) in g.productions_iterator() if len(bc) == 1 and bc[0] == w[i-1]}

    for j in range(2, n+1):
        for i in range(1, n-j+2):
            v[i, j] = set()
            for k in range(1, j):
                v[i, j] = v[i, j].union({a for (a, bc) in g.productions_iterator()
                                           if len(bc) == 2 and bc[0] in v[i, k] and bc[1] in v[i+k, j-k]})

    return v


def cyk(g: Grammar, w: Word) -> bool:
    n = len(w)
    v = cyk_table(g, w)

    return g.s in v[1, n]


def hamming_distance(wt: Word, wg: Word) -> float:
    # Modificado para que sea sobre 1
    # sum(wt[i] != wg[i] for i in range(min(len(wt), len(wg)))) + abs(len(wt) - len(wg)) / 2
    return (sum(wt[i] != wg[i] for i in range(min(len(wt), len(wg)))) + abs(len(wt) - len(wg))) / max(len(wt), len(wg))


def cyk_fitness(g: Grammar, w: Word) -> float:
    n = len(w)
    v = cyk_table(g, w)
    for i in range(n, 0):
        if any(g.s in v[j, i] for j in range(n-i+1, 0)):
            return i / n
    return 0


def fitness(g: Grammar, w: Word, positive: bool, th: Optional[int] = None) -> float:
    if th is None:
        th = len(w)

    if positive:
        if cyk(g, w):
            return 1
        elif (err := cyk_fitness(g, w)) > 0:
            return err
        else:
            return 0
            #iterator = grammar_iterator(non_terminal, terminal, g, s, max_length=len(w) + th)
            #best = 1
            #wg = next(iterator, None)
            #while wg is not None and len(wg) < len(w) + th:
            #    best = min(best, hamming_distance(w, wg))
            #    wg = next(iterator, None)
            #return 1 - best
    else:
        return int(not cyk(g, w))


def cases_generator(g: Grammar, n: Optional[int] = None) -> Iterator[Tuple[Word, bool]]:
    words = 0
    size = 1
    while n is None or words < n:
        for word in product(g.terminal, repeat=size):
            yield word, cyk(g, list(word))
            words += 1
        size += 1
