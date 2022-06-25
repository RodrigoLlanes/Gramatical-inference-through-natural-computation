import json
import os

from fitness import balanced_cases
from grammar import Grammar


def build_cases(n_positives: int, n_negatives: int, grammar_path: str, out_path: str) -> None:
    n = n_positives + n_negatives
    pos, neg = balanced_cases(Grammar.load(grammar_path), n, n_positives / n)
    out = {'positive': [case[0] for case in pos],
           'negative': [case[0] for case in neg],
           'grammar_path': os.path.realpath(grammar_path)}

    with open(out_path, 'w') as f:
        json.dump(out, f, indent=4)