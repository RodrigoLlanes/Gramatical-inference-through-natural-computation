import heapq
import random
from collections import defaultdict
from copy import copy
from pprint import pprint
from typing import Set, Dict, Union, Tuple, List, Iterator, Optional

Symbol = str
Word = List[Symbol]
Grammar = Dict[Symbol, Set[Union[Tuple[Symbol], Tuple[Symbol, Symbol]]]]


def random_grammar(non_terminal: Set[Symbol], terminal: Set[Symbol], n_non_term: int, n_terminal: int) -> Grammar:
    non_term, term = list(non_terminal), list(terminal)
    rules = set()
    grammar = defaultdict(lambda: set())

    while len(rules) < n_non_term:
        rule = (random.choice(non_term), random.choice(non_term), random.choice(non_term))
        rules.add(rule)

    while len(rules) < n_non_term + n_terminal:
        rule = (random.choice(non_term), random.choice(term))
        rules.add(rule)

    for rule in rules:
        grammar[rule[0]].add(tuple(list(rule)[1:]))

    return dict(grammar)


def cyk(g: Grammar, s: Symbol, w: Word) -> bool:
    n = len(w)
    v = dict()

    for i in range(1, n+1):
        v[i, 1] = {a for (a, bcs) in g.items() for bc in bcs if len(bc) == 1 and bc[0] == w[i-1]}

    for j in range(2, n+1):
        for i in range(1, n-j+2):
            v[i, j] = set()
            for k in range(1, j):
                v[i, j] = v[i, j].union({a for (a, bcs) in g.items()
                                           for bc in bcs
                                           if len(bc) == 2 and bc[0] in v[i, k] and bc[1] in v[i+k, j-k]})

    return s in v[1, n]


def hamming_distance(wt: Word, wg: Word) -> float:
    # Modificado para que sea sobre 1
    # sum(wt[i] != wg[i] for i in range(min(len(wt), len(wg)))) + abs(len(wt) - len(wg)) / 2
    return (sum(wt[i] != wg[i] for i in range(min(len(wt), len(wg)))) + abs(len(wt) - len(wg))) / max(len(wt), len(wg))


def valid_grammar(g: Grammar, s: Symbol) -> bool:
    heap = [s]
    valid = []
    waiting = []
    while len(heap):
        k = heap.pop()
        if k not in g:
            return False
        elif any(len(p) == 1 for p in g[k]):
            valid.append(k)
            heap.extend(symbol for symbol in set(sum([list(p) for p in g[k] if len(p) == 2], []))
                               if symbol not in valid and symbol not in waiting)
        elif any(len(p) == 2 and p[0] != k and p[0] not in waiting
                             and p[1] != k and p[1] not in waiting for p in g[k]):
            waiting.append(k)
            heap.extend(symbol for symbol in set(sum([list(p) for p in g[k] if len(p) == 2], []))
                               if symbol not in valid and symbol not in waiting)
        else:
            return False

    return True


def random_word(non_terminal: Set[Symbol], g: Grammar, s: Symbol) -> Word:
    w = [s]
    while any(wi in non_terminal for wi in w):
        index = random.choice([i for i in range(len(w)) if w[i] in non_terminal])
        w = w[:index] + list(random.choice(list(g[w[index]]))) + w[index+1:]
    return w


def grammar_iterator(non_terminal: Set[Symbol], terminal: Set[Symbol], g: Grammar, s: Symbol, max_length: Optional[int] = None) -> Iterator[Word]:
    heap = []
    visited = set()
    heapq.heappush(heap, (0, [s]))
    while len(heap):
        l, w = heapq.heappop(heap)
        # print(len(w), max_length, ''.join(w))
        for index in [i for i in range(len(w)) if w[i] in non_terminal]:
            for p in g[w[index]]:
                nw = w[:index] + list(p) + w[index+1:]
                if tuple(nw) in visited or (max_length is not None and len(nw) >= max_length):
                    continue
                elif all(wi in terminal for wi in nw):
                    visited.add(tuple(nw))
                    yield nw
                else:
                    visited.add(tuple(nw))
                    heapq.heappush(heap, (l+1, nw))


def fitness(non_terminal: Set[Symbol], terminal: Set[Symbol], g: Grammar, s: Symbol, w: Word, positive: bool, th: Optional[int] = None) -> float:
    if th is None:
        th = len(w)

    if positive:
        if cyk(g, s, w):
            return 1
        else:
            iterator = grammar_iterator(non_terminal, terminal, g, s, max_length=len(w) + th)
            best = 1
            wg = next(iterator, None)
            while wg is not None and len(wg) < len(w) + th:
                best = min(best, hamming_distance(w, wg))
                wg = next(iterator, None)
            return 1 - best
    else:
        return int(not cyk(g, s, w))


def encode(g: Grammar) -> List[Symbol]:
    gen = []
    for a, p in g.items():
        for k in p:
            gen.extend([a] + list(k))
    return gen


def split_gen(terminal: Set[Symbol], gen: List[Symbol]) -> List[List[Symbol]]:
    rest = copy(gen)
    res = []
    while len(rest):
        if rest[1] in terminal:
            res.append(rest[:2])
            rest = rest[2:]
        else:
            res.append(rest[:3])
            rest = rest[3:]
    return res


def decode(terminal: Set[Symbol], gen: List[Symbol]) -> Grammar:
    grammar = defaultdict(lambda: set())
    for p in split_gen(terminal, gen):
        grammar[p[0]].add(tuple(p[1:]))
    return dict(grammar)


def random_combination(terminal: Set[Symbol], a: List[Symbol], b: List[Symbol]) -> List[Symbol]:
    a_split, b_split = split_gen(terminal, a), split_gen(terminal, b)
    index = random.randrange(0, min(len(a_split), len(b_split)))
    return sum(a_split[:index] + b_split[index:], [])


def random_simple_mutations(non_terminal: Set[Symbol], terminal: Set[Symbol], gen: List[Symbol], n_mutations: int = 1) -> List[Symbol]:
    indexes = random.choices(list(range(len(gen))), k=n_mutations)
    res = copy(gen)
    for i in indexes:
        if res[i] in terminal:
            res[i] = random.choice(list(terminal))
        else:
            res[i] = random.choice(list(non_terminal))
    return res


def test():
    terminal = {'a', 'b'}
    non_term = {'S', 'A', 'B', 'C'}
    g = random_grammar(non_term, terminal, 3, 2)
    print("Random Grammar:", g)
    gen = encode(g)
    print("Encoded Grammar:", gen)
    g = decode(terminal, gen)
    print("Decoded Grammar:", g)
    print("Is a valid grammar:", valid_grammar(g, 'S'))
    assert valid_grammar(g, 'S')
    w = random_word(non_term, g, 'S')
    print("Random word from that grammar:", w)
    print("Is that word generated by the grammar:", cyk(g, 'S', w))
    it = grammar_iterator(non_term, terminal, g, 'S')
    print("Five words from that grammar:")
    for _ in range(5):
        w = next(it, None)
        if w is None:
            break
        print("    ", w)


def main():
    # test()
    s = 'A'
    non_terminal = {chr(ord('A') + i) for i in range(5)}
    terminal = {chr(ord('a') + i) for i in range(2)}

    grammars = [random_grammar(non_terminal, terminal, 18, 2) for _ in range(20)]
    grammars = [grammar for grammar in grammars if valid_grammar(grammar, s)]

    non_term_t = {'A', 'B', 'C', 'D'}
    terminal_t = {'a', 'b'}
    grammar_t = {'A': {('B','C')},
                 'B': {('a',)},
                 'C': {('b',), ('A', 'D')},
                 'D': {('b',)}}

    samples = []
    for _ in range(5):
        w = random_word(non_term_t, grammar_t, 'A')
        while len(w) > 7:
            w = random_word(non_term_t, grammar_t, 'A')
        samples.append(w)

    for w in samples:
        print(w)
        bests = sorted(grammars, key=lambda g: fitness(non_terminal, terminal, g, 'A', w, True, th=0))
        print(fitness(non_terminal, terminal, bests[0], 'A', w, True), bests[0])


if __name__ == '__main__':
    main()
