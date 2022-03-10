from grammar import Grammar

from math import floor, ceil
from itertools import product
from random import sample, choices, randint
from typing import Set, Dict, Tuple, List, Optional, Generator

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


def cases_generator(g: Grammar, n: Optional[int] = None) -> Generator[Tuple[Word, bool], None, None]:
    words = 0
    size = 1
    while n is None or words < n:
        for word in product(g.terminal, repeat=size):
            yield word, cyk(g, list(word))
            words += 1
        size += 1


def balanced_cases(g: Grammar, n: int, positive_rate: Optional[float] = 0.5) -> List[Tuple[Word, bool]]:
    it = g.words_iterator()
    positives = [(next(it), True) for _ in range(floor(n * positive_rate))]

    # Error checking
    rest = 0
    max_size = len(positives[-1])
    terminals = list(g.terminal)
    while True:
        print(len(terminals) ** max_size, rest, len(positives), ceil(n * (1 - positive_rate)))
        while len(word := next(it)) == max_size:
            rest += 1
        if len(terminals) ** max_size - rest - len(positives) >= ceil(n * (1 - positive_rate)):
            break
        max_size = len(word)
        rest += 1

    print("NEGATIVES")
    negatives = set()
    while len(negatives) <  ceil(n * (1 - positive_rate)):
        word = choices(terminals, k=randint(1, max_size))
        if not cyk(g, word):
            negatives.add((tuple(word), False))
    return list(negatives) + positives

    """
    positives, negatives = [], []
    for word, positive in cases_generator(g):
        if len(positives) / positive_rate >= n:
            return sample(negatives, floor(n * (1-positive_rate))) + sample(positives, ceil(n * positive_rate))
        if positive:
            positives.append((word, positive))
        else:
            negatives.append((word, positive))
    """

