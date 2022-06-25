import os
import time
import argparse

from tissue import Tissue
from grammar import Grammar
from fitness import balanced_cases

import json
from math import ceil, floor
from tqdm import trange
from copy import deepcopy
from random import shuffle
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional

from tools.cases_builder import build_cases
from tools.experiments_visualization import visualize_experiment
from tools.latex_generator import generate_latex

Symbol = str
Word = List[Symbol]


def build_tissue(n_non_term_sym: int, n_terminal_sym: int, n_non_term_prod: int, n_terminal_prod: int, n_grammars: int, n_cells: int) -> Tissue:
    non_terminal = {chr(ord('A') + i) for i in range(n_non_term_sym)}.union({'S'})
    if len(non_terminal) < n_non_term_sym:
        non_terminal.add(chr(ord(max(non_terminal))+1))
    terminal = {chr(ord('a') + i) for i in range(n_terminal_sym)}
    return Tissue(non_terminal, terminal, 'S', n_non_term_prod, n_terminal_prod, n_cells, n_grammars)


def make_cases(grammar: Grammar, n_cases: int, positive_rate: float, train_rate: float) -> Tuple[List[Tuple[Word, bool]], List[Tuple[Word, bool]]]:
    pos, neg = balanced_cases(grammar, n_cases, positive_rate)
    cases = pos + neg
    shuffle(cases)
    train_i = int(n_cases * train_rate)
    return cases[:train_i], cases[train_i:]


def load_cases(path: str) -> List[Tuple[Word, bool]]:
    with open(path, 'r') as f:
        data = json.load(f)
        cases = [(w, True) for w in data['positive']] + [(w, False) for w in data['negative']]
        shuffle(cases)
        return cases


def train_and_test(tissue: Tissue, train_cases: List[Tuple[Word, bool]], test_cases: List[Tuple[Word, bool]],
                   n_crossovers: int, n_mutations: int, mutation_size_range: Tuple[int, int], mutate_out: Optional[bool] = False,
                   epochs: Optional[int] = 1, batch_size: Optional[int] = 1, shuffle_epochs: Optional[bool] = False,
                   enable_trace: Optional[bool] = False, verb: Optional[bool] = False) -> Tuple[Grammar, float, List[float]]:
    n_batches = ceil(len(train_cases)/batch_size)
    trace = []
    for _ in trange(1, epochs + 1) if verb else range(1, epochs + 1):
        if shuffle_epochs: shuffle(train_cases)
        for i in trange(n_batches, leave=False) if verb else range(n_batches):
            tissue.train_step(train_cases[i*batch_size:(i+1)*batch_size], n_crossovers, n_mutations, mutation_size_range, mutate_out=mutate_out)
            if enable_trace:
                trace.append(tissue.best(test_cases)[1])

    if verb: print('Testing and scoring')
    best, fit = tissue.best(test_cases)
    return best, fit, trace


def combinations(src: dict) -> List[dict]:
    out = [{}]
    for k, v in src.items():
        if isinstance(v, list):
            curr, out = out, []
            for d in curr:
                for vs in v:
                    d[k] = vs
                    out.append(deepcopy(d))
        else:
            for d in out:
                d[k] = v
    return out



def run_exp_original(path: str, cases_path: str, verb: Optional[bool] = False, enable_trace: Optional[bool] = False, repetitions: Optional[int] = 1) -> List[dict]:
    out = []
    if verb: print('Loading cases')
    cases = load_cases(cases_path)
    cases_size = len(cases)
    with open(path, 'r') as f:
        data = json.load(f)
        for _ in range(repetitions):
            for params in combinations(data):
                if verb: print(f'Parameters: {params}')
                out.append({'params': deepcopy(params)})
                params['mutation_size_range'] = (params['mutation_size_min'], params['mutation_size_max'])

                if verb: print('Generating grammars')
                tissue = build_tissue(params['n_non_term_sym'], params['n_terminal_sym'], params['n_non_term_prod'], params['n_terminal_prod'], params['n_grammars'], params['n_cells'])

                train_cases, test_cases = cases[:int(cases_size * 0.5)], cases[int(cases_size * 0.5):]

                if verb: print('Starting train')
                best, fit, trace = train_and_test(tissue, train_cases, test_cases, params['n_crossovers'], params['n_mutations'],
                                                  params['mutation_size_range'],
                                                  params['mutate_out'], params['epochs'], params['batch_size'], params['shuffle_epochs'], enable_trace, verb)

                if enable_trace: out[-1]['trace'] = trace
                out[-1]['fitness'] = fit
                out[-1]['result'] = best.serializable()
                if verb:
                    print('\nBest grammar:')
                    print(f'Score {fit}')
                    print(best)

                if enable_trace:
                    plt.plot(trace)
                    plt.show()
    return out



def run_exp(path: str, cases_path: str, verb: Optional[bool] = False, enable_trace: Optional[bool] = False, repetitions: Optional[int] = 1) -> List[dict]:
    out = []
    cases = load_cases(cases_path)
    with open(path, 'r') as f:
        data = json.load(f)
        for _ in range(repetitions):
            for basic_params in combinations(data):
                print(basic_params)
                if verb: print('Loading cases')
                size = basic_params['samples_size']
                for i in range(len(cases) // size):
                    params = deepcopy(basic_params)
                    train_cases = cases[i * size: (i + 1) * size]
                    test_cases = cases[:i * size] + cases[(i + 1) * size:]
                    if verb: print(f'Parameters: {params}')
                    out.append({'params': deepcopy(params)})
                    #params['grammar'] = Grammar.load(params['grammar'])
                    params['mutation_size_range'] = (params['mutation_size_min'], params['mutation_size_max'])

                    if verb: print('Generating grammars')
                    tissue = build_tissue(params['n_non_term_sym'], params['n_terminal_sym'], params['n_non_term_prod'], params['n_terminal_prod'], params['n_grammars'], params['n_cells'])


                    if verb: print('Starting train')
                    best, fit, trace = train_and_test(tissue, train_cases, test_cases, params['n_crossovers'], params['n_mutations'],
                                                      params['mutation_size_range'],
                                                      params['mutate_out'], params['epochs'], params['batch_size'], params['shuffle_epochs'], enable_trace, verb)

                    if enable_trace: out[-1]['trace'] = trace
                    out[-1]['fitness'] = fit
                    out[-1]['result'] = best.serializable()
                    if verb:
                        print('\nBest grammar:')
                        print(f'Score {fit}')
                        print(best)

                    if enable_trace:
                        plt.plot(trace)
                        plt.show()
    return out


def experiment_main(exp_path: str, cases_path: str, out_path: str, verb: bool, repetitions: int) -> None:
    enable_trace = False

    out = run_exp(exp_path, cases_path, verb, enable_trace, repetitions=repetitions)
    with open(out_path, 'w') as f:
        json.dump({
            'cases_path': os.path.realpath(cases_path),
            'experiment_path': os.path.realpath(exp_path),
            'results': out
        }, f, indent=4)


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = True

    # Subparser for case builder tool
    parser_cbuilder = subparsers.add_parser('cbuilder')
    parser_cbuilder.add_argument('grammar', help='path to the grammar file (json)')
    parser_cbuilder.add_argument('positives', type=int, help='number of positive cases')
    parser_cbuilder.add_argument('negatives', type=int, help='number of negative cases')
    parser_cbuilder.add_argument('out', help='path to the output cases file (json)')

    # Subparser for experiments
    parser_experiment = subparsers.add_parser('exp')
    parser_experiment.add_argument('experiment', help='experiment to be run (json)')
    parser_experiment.add_argument('cases', help='cases file (json) to use in the experiment')
    parser_experiment.add_argument('out', help='path to the output results file (json)')
    parser_experiment.add_argument('-v', '--verbose', action='store_true', help='increase verbosity')
    parser_experiment.add_argument('-r', '--repetitions', type=int, default=1, help='number of times the experiment is repeated (default 1)')

    # Subparser for results visualizer
    parser_visualizer = subparsers.add_parser('plot')
    parser_visualizer.add_argument('file', help='path to the results file (json) or directory to plot')
    parser_visualizer.add_argument('-m', '--mode', choices=['err', 'box', 'dot'], default='box', help='plot mode (default box)')

    # Subparser for results visualizer
    parser_latex = subparsers.add_parser('latex')
    parser_latex.add_argument('table', help='path to the output table file (latex)')
    parser_latex.add_argument('plot', help='path to the output plot file (latex)')
    parser_latex.add_argument('-f', '--files', action='append', nargs='+', required=True, help='paths to the results files for generate the table and plot')

    args = parser.parse_args()
    config = vars(args)

    if config['subcommand'] == 'cbuilder':
        build_cases(config['positives'], config['negatives'], config['grammar'], config['out'])
    elif config['subcommand'] == 'exp':
        experiment_main(config['experiment'], config['cases'], config['out'], config['verbose'], config['repetitions'])
    elif config['subcommand'] == 'plot':
        visualize_experiment(config['file'], config['mode'])
    elif config['subcommand'] == 'latex':
        generate_latex(config['files'][0], config['plot'], config['table'])


if __name__ == '__main__':
    main()
