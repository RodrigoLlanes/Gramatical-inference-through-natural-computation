from grammar import Grammar
from fitness import fitness
from genome import random_combination, random_simple_mutations

from typing import List
from random import choices,randint


Symbol = str
Word = List[Symbol]


def main():
    n_non_term_sym = 5
    n_terminal_sym = 2
    n_non_term_prod = 18
    n_terminal_prod = 2
    n_grammars = 20
    n_cells = 5
    n_crossovers = 5
    n_mutations = 5
    mutation_size_range = (1, 10)


    # test()
    s = 'A'
    non_terminal = {chr(ord('A') + i) for i in range(n_non_term_sym)}
    terminal = {chr(ord('a') + i) for i in range(n_terminal_sym)}

    tissue = []
    out_cell = []
    for _ in range(n_cells):
        grammars = [Grammar.random(non_terminal, terminal, n_non_term_prod, n_terminal_prod) for _ in range(n_grammars)]
        grammars = [grammar.encoded() for grammar in grammars if grammar.is_valid()]
        tissue.append(grammars)

    non_term_t = {'A', 'B', 'C', 'D'}
    terminal_t = {'a', 'b'}
    grammar_t = {'A': {('B','C')},
                 'B': {('a',)},
                 'C': {('b',), ('A', 'D')},
                 'D': {('b',)}}
    train_cases = [(('a', 'b'), True), (('a', 'b', 'a'), False), (('b', 'b'), False), (('a', 'a', 'b', 'b'), True), (('a', 'a', 'a', 'b', 'b', 'b'), True)]
    test_cases = [(('a', 'a'), False), (('a', 'b', 'b'), False), (('b', 'a', 'b'), False), (('a', 'a', 'a', 'a', 'b', 'b', 'b', 'b'), True), (('a', 'a', 'a', 'a', 'a', 'b', 'b', 'b', 'b', 'b'), True)] + train_cases

    for word, positive in train_cases:
        print(word)
        for i, cell in enumerate(tissue):
            cell.sort(key=lambda genome: fitness(Grammar.decode(non_terminal, terminal, s, genome), word, positive), reverse=True)
            out_cell.append(cell[0])
            crossed = [random_combination(terminal, a, b) for a, b in [choices(cell, k=2) for _ in range(n_crossovers)]]
            mutated = [random_simple_mutations(non_terminal, terminal, gen, randint(mutation_size_range[0], mutation_size_range[1])) for gen in choices(cell, k=n_mutations)]
            tissue[i] = mutated + crossed + cell[:n_grammars - n_mutations - n_crossovers]

    best = sorted(out_cell, key=lambda genome: sum(fitness(Grammar.decode(non_terminal, terminal, s, genome), word, positive) for word, positive in test_cases), reverse=True)[0]
    decoded = Grammar.decode(non_terminal, terminal, s, best)
    fit = sum(fitness(decoded, word, positive) for word, positive in test_cases) / len(test_cases)
    print('')
    print(sorted([sum(fitness(Grammar.decode(non_terminal, terminal, s, genome), word, positive) for word, positive in test_cases) / len(test_cases) for genome in out_cell], reverse=True))
    print(fit)
    print(decoded)

if __name__ == '__main__':
    main()
