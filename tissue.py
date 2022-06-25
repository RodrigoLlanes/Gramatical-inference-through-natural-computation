from __future__ import annotations

import random
from itertools import repeat

from grammar import Grammar
from fitness import fitness, multiple_fitness
from genome import random_combination, random_simple_mutations

import multiprocessing
from functools import partialmethod
from random import choices, randint
from typing import Set, Dict, Union, Tuple, List, Optional, Callable


Symbol = str
Word = List[Symbol]
Productions = Dict[Symbol, Set[Union[Tuple[Symbol], Tuple[Symbol, Symbol]]]]


class Membrane:
    def __init__(self, non_terminal: Set[Symbol], terminal: Set[Symbol], s: Symbol, n_non_term_prod: int, n_terminal_prod: int, n_grammars: int, empty: Optional[bool] = False) -> None:
        self.s : Symbol = s
        self.terminal : Set[Symbol] = terminal
        self.non_terminal : Set[Symbol] = non_terminal

        self.n_grammars : int = n_grammars

        self.grammars : List[List[Symbol]] = []
        if not empty:
            self.grammars = [Grammar.random(non_terminal, terminal, s, n_non_term_prod, n_terminal_prod).encoded() for _ in range(n_grammars)]

    def decode(self, gen: List[Symbol]) -> Grammar:
        return Grammar.decode(self.non_terminal, self.terminal, self.s, gen)


    def train_step(self, cases: List[Tuple[Word, bool]], n_crossovers: int, n_mutations: int, mutation_size_range: Tuple[int, int]) -> List[Symbol]:
        self.grammars.sort(key=lambda g: multiple_fitness(self.decode(g), cases), reverse=True)
        best = self.grammars[0]
        crossed = [random_combination(self.terminal, a, b)
                   for a, b in [choices(self.grammars, k=2) for _ in range(n_crossovers)]]
        mutated = [random_simple_mutations(self.non_terminal, self.terminal, gen, randint(mutation_size_range[0], mutation_size_range[1]))
                   for gen in choices(self.grammars, k=n_mutations)]
        self.grammars = mutated + crossed + self.grammars[:self.n_grammars - n_mutations - n_crossovers]
        return best

    def best(self, test_cases: List[Tuple[Word, bool]]) -> Tuple[Grammar, float]:
        scored = sorted(self.grammars, key=lambda g: multiple_fitness(self.decode(g), test_cases), reverse=True)
        decoded = self.decode(scored[0])
        fit = sum(fitness(decoded, word, positive) for word, positive in test_cases) / len(test_cases)
        return decoded, fit


class Tissue:
    def __init__(self, non_terminal: Set[Symbol], terminal: Set[Symbol], s: Symbol, n_non_term_prod: int, n_terminal_prod: int, n_cells: int, n_grammars: int) -> None:
        self.s : Symbol = s
        self.terminal : Set[Symbol] = terminal
        self.non_terminal : Set[Symbol] = non_terminal

        self.n_grammars : int = n_grammars

        self.membranes : List[Membrane] = [Membrane(non_terminal, terminal, s, n_non_term_prod, n_terminal_prod, n_grammars) for _ in range(n_cells)]
        self.out : Membrane = Membrane(non_terminal, terminal, s, n_non_term_prod, n_terminal_prod, n_grammars, empty=True)

    def aux(self, membrane: Membrane, cases: List[Tuple[Word, bool]], n_crossovers: int, n_mutations: int, mutation_size_range: Tuple[int, int]) -> List[str]:
        return membrane.train_step(cases, n_crossovers, n_mutations, mutation_size_range)

    def train_step(self, cases: List[Tuple[Word, bool]], n_crossovers: int, n_mutations: int, mutation_size_range: Tuple[int, int], mutate_out: Optional[bool] = False) -> None:
        for membrane in self.membranes:
            self.out.grammars.append(membrane.train_step(cases, n_crossovers, n_mutations, mutation_size_range))
        if mutate_out:
            self.out.train_step(cases, n_crossovers, n_mutations, mutation_size_range)


    def best(self, test_cases: List[Tuple[Word, bool]]) -> Tuple[Grammar, float]:
        return self.out.best(test_cases)
