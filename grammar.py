from __future__ import annotations

import heapq
from random import choice
from genome import split_gen
from collections import defaultdict
from functools import singledispatchmethod
from typing import Set, Dict, Union, Tuple, List, Generator, Optional


Symbol = str
Word = List[Symbol]
Productions = Dict[Symbol, Set[Union[Tuple[Symbol], Tuple[Symbol, Symbol]]]]


class GrammarException(Exception):
    """Base class for grammar exceptions"""
    pass


class Grammar:
    def __init__(self, non_terminal: Set[Symbol], terminal: Set[Symbol], productions: Productions, s: Symbol) -> None:
        self.non_terminal: Set[Symbol] = non_terminal
        self.terminal: Set[Symbol] = terminal
        self.productions: Productions = productions
        self.s: Symbol = s

    def __contains__(self, symbol: Symbol):
        return symbol in self.productions

    def __getitem__(self, symbol: Symbol):
        return self.productions[symbol]

    def __repr__(self):
        out = ''
        size = max(len(s) for s in self.non_terminal.union(self.terminal))
        for k, v in self.productions.items():
            out += f'{k:{size}} -> '
            for i, right in enumerate(v):
                if i != 0:
                    out += ' ' * size + '  | '
                out += ' '.join(f'{s:{size}}' for s in right) + '\n'
        return out

    @staticmethod
    def random(non_terminal: Set[Symbol], terminal: Set[Symbol], n_non_term_prod: int, n_term_prod: int) -> Grammar:
        non_term, term = list(non_terminal), list(terminal)

        rules = set()
        grammar = defaultdict(lambda: set())

        while len(rules) < n_non_term_prod:
            rule = (choice(non_term), choice(non_term), choice(non_term))
            rules.add(rule)

        while len(rules) < n_non_term_prod + n_term_prod:
            rule = (choice(non_term), choice(term))
            rules.add(rule)

        for rule in rules:
            grammar[rule[0]].add(tuple(list(rule)[1:]))

        return Grammar(set(non_term), set(term), grammar, 'A')

    @staticmethod
    def decode(non_terminal: Set[Symbol], terminal: Set[Symbol], s: Symbol, gen: List[Symbol]) -> 'Grammar':
        grammar = defaultdict(lambda: set())
        for p in split_gen(terminal, gen):
            grammar[p[0]].add(tuple(p[1:]))
        return Grammar(non_terminal, terminal, grammar, s)

    def is_valid(self) -> bool:
        heap = [self.s]
        valid = []
        waiting = []
        while len(heap):
            k = heap.pop()
            if k not in self:
                return False
            elif any(len(p) == 1 for p in self[k]):
                valid.append(k)
                heap.extend(symbol for symbol in set(sum([list(p) for p in self[k] if len(p) == 2], []))
                            if symbol not in valid and symbol not in waiting)
            elif any(len(p) == 2 and p[0] != k and p[0] not in waiting
                     and p[1] != k and p[1] not in waiting for p in self[k]):
                waiting.append(k)
                heap.extend(symbol for symbol in set(sum([list(p) for p in self[k] if len(p) == 2], []))
                            if symbol not in valid and symbol not in waiting)
            else:
                return False

        return True

    def words_iterator(self, max_length: Optional[int] = None) -> Generator[Word, None, None]:
        heap = []
        visited = set()
        heapq.heappush(heap, (0, [self.s]))
        while len(heap):
            l, w = heapq.heappop(heap)
            for index in [i for i in range(len(w)) if w[i] in self.non_terminal]:
                for p in self[w[index]]:
                    nw = w[:index] + list(p) + w[index+1:]
                    if tuple(nw) in visited or (max_length is not None and len(nw) >= max_length):
                        continue
                    elif all(wi in self.terminal for wi in nw):
                        visited.add(tuple(nw))
                        yield nw
                    else:
                        visited.add(tuple(nw))
                        heapq.heappush(heap, (l+1, nw))

    def encoded(self) -> List[Symbol]:
        gen = []
        for a, p in self.productions.items():
            for k in p:
                gen.extend([a] + list(k))
        return gen

    def random_word(self) -> Word:
        w = [self.s]
        while any(wi in self.non_terminal for wi in w):
            index = choice([i for i in range(len(w)) if w[i] in self.non_terminal])
            w = w[:index] + list(choice(list(self[w[index]]))) + w[index + 1:]
        return w

    def productions_iterator(self) -> Tuple[Symbol, Set[Union[Tuple[Symbol], Tuple[Symbol, Symbol]]]]:
        for k, v in self.productions.items():
            for prod in v:
                yield k, prod
