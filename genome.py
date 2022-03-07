import random
from copy import copy
from typing import Set, List


Symbol = str


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