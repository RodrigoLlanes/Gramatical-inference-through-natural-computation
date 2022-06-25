from math import floor, ceil
from itertools import product
from random import choices, randint
from typing import Set, Dict, Tuple, List, Optional, Generator, TypeVar, Callable

from grammar import Grammar


Symbol = str
Word = List[Symbol]
T = TypeVar('T')


def cyk_table(g: Grammar, w: Word) -> Dict[Tuple[int, int], Set[Symbol]]:
    n = len(w)
    v = {}

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


def print_cyk_table(table: Dict[Tuple[int, int], Set[Symbol]], w: Word):
    n = len(w)
    max_cell_size = max(len(v) for v in table.values())
    for j in range(1, n + 1):
        print(f'{j}: ', end='')
        for i in range(1, n - j + 2):
            cont = ''.join(table[i, j])
            print('[' + cont + (max_cell_size - len(cont)) * ' ' + '] ', end='')
        print('')

def cyk_fitness(g: Grammar, w: Word) -> float:
    n = len(w)
    v = cyk_table(g, w)
    for j in range(n, 0, -1):
        if any(g.s in v[i, j] for i in range(1, n-j+2)):
            return j / n
    return 0


def fitness(g: Grammar, w: Word, positive: bool) -> float:
    fit = cyk_fitness(g, w)
    fit = fit if positive else 1 - fit
    return fit


def multiple_fitness(g: Grammar, cases: List[Tuple[Word, bool]]) -> float:
    # print(g.serializable())
    # print(''.join(str(fitness(g, w, p)) for w, p in cases))
    return sum(fitness(g, w, p) for w, p in cases)


def cases_generator(g: Grammar, n: Optional[int] = None) -> Generator[Tuple[Word, bool], None, None]:
    words = 0
    size = 1
    while n is None or words < n:
        for word in product(g.terminal, repeat=size):
            yield word, cyk(g, list(word))
            words += 1
        size += 1


def balanced_cases(g: Grammar, n: int, positive_rate: Optional[float] = 0.5) -> Tuple[List[Tuple[Word, bool]],  List[Tuple[Word, bool]]]:
    it = g.words_iterator()
    positives = [(next(it), True) for _ in range(floor(n * positive_rate))]

    # Error prevention
    rest = len(positives)
    terminals = list(g.terminal)
    word = positives[-1][0]
    max_size = len(word) - 1
    while len(terminals) ** max_size - rest < ceil(n * (1 - positive_rate)):
        max_size = len(word)
        while len(word := next(it)) == max_size:
            rest += 1
        max_size = len(word) - 1
        rest += 1

    # CYK es muy caro para palabras grandes, se podría implementar la opción de facilitar un checker definido en python
    negatives = set()
    while len(negatives) <  ceil(n * (1 - positive_rate)):
        word = choices(terminals, k=randint(1, max_size))
        if not cyk(g, word):
            negatives.add((tuple(word), False))
    return positives, list(negatives)


def chunks(l: List[T], chunk_size: int) -> List[List[T]]:
    return [l[i: i+chunk_size] for i in range(0, len(l), chunk_size)]
