import json
import os.path
from os import listdir
from pathlib import Path
from statistics import mean
from typing import Optional, Callable, List

import matplotlib.pyplot as plt
from collections import defaultdict


def get_params(exp_path: str) -> List[str]:
    with open(exp_path, 'r') as f:
        data = json.load(f)
        return [k for k, v in data.items() if isinstance(v, list) and len(v) > 0]

def get_language(cases_path: str) -> str:
    with open(cases_path, 'r') as f:
        data = json.load(f)
        with open(data['grammar_path'], 'r') as gf:
            grammar_data = json.load(gf)
            if 'name' in grammar_data:
                return grammar_data['name']
            else:
                return data['grammar_path'].split('.')[0].split(os.path.sep)[-1]

def plot(path: str, mode: Optional[str] = 'box') -> None:
    # mode: ['box', 'err', 'dot']

    def by_params(*args):
        def f(case):
            out = []
            for p in args:
                out.append(case['params'][p])
            return tuple(out)

        return f

    with open(path, 'r') as f:
        data = json.load(f)

        language = get_language(data['cases_path'])
        params = get_params(data['experiment_path'])
        key_func = by_params(*params)

        res = defaultdict(list)
        for case in data['results']:
            k = key_func(case)
            res[k].append(case['fitness'])

        keys = sorted(res.keys())
        data = [res[k] for k in keys]

        # plot:
        fig, ax = plt.subplots()
        fig.set_figwidth(len(keys))
        ax.set_xlabel(', '.join(params))
        ax.set_ylabel('Accuracy')
        ax.set_title(f'{language}\nAccuracy / ({", ".join(params)})')

        if mode == 'err':
            x = keys
            y = [mean(res[k]) for k in x]
            err = [[abs(max(res[k]) - y[i]) for i, k in enumerate(x)], [abs(min(res[k]) - y[i]) for i, k in enumerate(x)]]
            ax.errorbar(range(len(x)), y, err, fmt='o', linewidth=2, capsize=6)
            plt.xticks(range(len(x)), x)
        elif mode == 'box':
            ax.boxplot(data)
            ax.set_xticklabels(keys)
        elif mode == 'dot':
            y = sum([res[k] for k in keys], [])
            x = sum([[i] * len(res[k]) for i, k in enumerate(keys)], [])
            ax.plot(x, y, 'b+')
            ax.set_xticks(range(len(keys)))
            ax.set_xticklabels(keys)

        plt.show()


def plot_file(path: str, mode:str) -> None:
    plot(path, mode=mode)


def plot_dir(path: str, mode:str) -> None:
    for file in listdir(path):
        if file.endswith('.json'):
            plot_file(file, mode)


def visualize_experiment(path: str, mode:str) -> None:
    path_obj = Path(path)
    if path_obj.is_file():
        plot_file(path, mode)
    elif path_obj.is_dir():
        plot_dir(path, mode)
    else:
        print("Error: File or folder doesn't exists")
