import json
import os

import numpy as np
from os import listdir
from typing import Callable, List, Dict, Tuple

import statistics
from collections import defaultdict


def get_raw_params(exp_path: str) -> List[str]:
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


def format_params(params: List[str]) -> List[str]:
    def parse_param(param: str) -> str:
        return ' '.join(param.split('_')).capitalize()

    return list(map(parse_param, params))


def by_params(params: List[str]) -> Callable[[Dict], tuple]:
    def f(case):
        out = []
        for p in params:
            out.append(case['params'][p])
        return tuple(out)

    return f


def load_data(result_path: str) -> Tuple[str, List[str], Dict[tuple, List[float]]]:
    print(result_path)
    with open(result_path, 'r') as f:
        data = json.load(f)
        language = get_language(data['cases_path'])
        params = get_raw_params(data['experiment_path'])

        key_func = by_params(params)
        res = defaultdict(list)
        for case in data['results']:
            k = key_func(case)
            res[k].append(case['fitness'])

        return language, params, res


table_header_pattern = '''\
\\begin{center}
\\begin{tabular}{||$CS$||}  
    \hline
    Lenguaje & $ParamsNames$ & Mediana & Min. & Max. & $Q_1$ & $Q_3$  \\\\ [0.5ex] 
    \hline\
'''

table_row_pattern = '''
    \hline
    $Language$ & $ParamsValues$ & $Median$ & $Min$ & $Max$ & $Q1$ & $Q3$  \\\\\
'''

table_end_pattern = '''
    \hline
\end{tabular}
\end{center}\
'''

def load_statistics(pattern: str, data: List[float]) -> str:
    row = pattern.replace('$Median$', str(round(statistics.median(data), 4)))
    row = row.replace('$Min$', str(round(min(data), 4)))
    row = row.replace('$Max$', str(round(max(data), 4)))
    quantiles = [np.quantile(data, .25, method='midpoint'), np.quantile(data, .5, method='midpoint'), np.quantile(data, .75, method='midpoint')]

    row = row.replace('$Q1$', str(round(quantiles[0], 4)))
    row = row.replace('$Q3$', str(round(quantiles[2], 4)))
    return row


def load_table(data: Dict[tuple, List[float]], language: str) -> str:
    keys = sorted(data.keys())

    out = ''
    for k in keys:
        row = table_row_pattern.replace('$Language$', language)
        row = row.replace('$ParamsValues$', ' & '.join(map(str, k)))
        out += load_statistics(row, data[k])

    return out


plot_header_pattern = '''
\\begin{center}
    \\begin{tabular}{ | $LegendCS$ |}
        \\hline
        $Legend$ \\\\
        \\hline
    \\end{tabular}
\\end{center}
\\begin{center}
    \\begin{tikzpicture}
        \\begin{axis}[
            scale only axis,
            height=5cm,
            width=13cm,   
            boxplot/draw direction=y,
            xtick={$XTiks$},
            xticklabels={$XTiksLabels$},
            ylabel=Accuracy,
            xlabel=$XLabel$
        ]\
'''

plot_item_pattern = '''
        \\addplot+[
            draw=$DrawColor$,
            boxplot prepared={
                draw position = $Position$,
                median=$Median$,
                upper quartile=$Q3$,
                lower quartile=$Q1$,
                upper whisker=$Max$,
                lower whisker=$Min$
            },boxplot prepared
        ] coordinates {};\
'''

plot_end_pattern = '''
        \\end{axis}
    \\end{tikzpicture}
\\end{center}\
'''

plot_colors = ['red', 'blue', 'green', 'black', 'orange', 'yellow']


def format_keys(keys: tuple) -> str:
    if len(keys) == 1:
        return str(keys[0])

    return ' / '.join([str(key) for key in keys])


def generate_table(data: Dict[str, Dict[tuple, List[float]]], params: List[str]) -> str:
    table_out = ''
    header = table_header_pattern.replace("$CS$", " ".join(["c"] * (6 + len(params))))
    header = header.replace("$ParamsNames$", ' & '.join(format_params(params)))
    table_out += header

    for language, results in data.items():
        table_out += load_table(results, language)

    return table_out + table_end_pattern


def generate_plot(languages: List[str], keys: List[str], data: Dict[str, Dict[tuple, List[float]]], params: List[str]) -> str:
    plot_out = ''
    gap = 1
    n_languages = len(languages)
    tiks = [str((n_languages + 1) / 2 + (n_languages + gap) * i) for i in range(len(keys))]
    params_names = format_params(params)

    header = plot_header_pattern.replace('$XTiks$', ', '.join(tiks))
    header = header.replace('$XLabel$', format_keys(params_names))
    header = header.replace('$XTiksLabels$', ', '.join(map(format_keys, keys)))
    header = header.replace('$LegendCS$', " ".join(["c"] * (len(languages) * 3 - 1)))
    legend = []
    for i in range(len(languages)):
        legend.append('\\textcolor{' + plot_colors[i] + '}{$\\bullet$} & ' + languages[i])
    header = header.replace('$Legend$', ' & & '.join(legend))
    header = header.replace('$XLabel$', format_keys(params_names))
    plot_out += header

    for lang, experiment in data.items():
        for k, values in experiment.items():
            item = load_statistics(plot_item_pattern, values)
            item = item.replace('$DrawColor$', plot_colors[languages.index(lang)])
            item = item.replace('$Position$', str(keys.index(k) * (n_languages + gap) + languages.index(lang) + 1))
            plot_out += item

    return plot_out + plot_end_pattern


def generate_latex(paths: List[str], plot_path: str, table_path: str):
    data = {}
    prev = None
    for path in paths:
        language, params, results = load_data(path)
        if language in data:
            print(f"Error: Repeated experiment language {language}")
            return

        if prev is None:
            prev = params
        elif prev != params:
            print(f"Error: All the experiments must tweak the same parameters")
            return

        data[language] = results

    table_out = generate_table(data, params)
    with open(table_path, 'w', encoding='UTF8') as f:
        f.write(table_out)

    keys = set()
    for results in data.values():
        keys = keys.union(set(results.keys()))
    keys = list(sorted(keys))

    plot_out = generate_plot(list(sorted(data.keys())), keys, data, params)
    with open(plot_path, 'w', encoding='UTF8') as f:
        f.write(plot_out)
