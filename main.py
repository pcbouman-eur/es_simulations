# import igraph as ig
import numpy as np
import sys
import os
import json
from collections import Counter
from collections.abc import Iterable
import numbers
from matplotlib import pyplot as plt
from configuration.parser import get_arguments
from net_generation.base import init_sbm, add_zealots, planted_affinity
from simulation.base import run_symulation, run_thermalization
from electoral_sys.electoral_system import system_population_majority, system_district_majority


def plot_hist(distribution, name, suffix, output_dir='plots/', colors=('red', 'green', 'blue')):
    os.makedirs(output_dir, exist_ok=True)
    idx = 0
    for key in sorted(distribution.keys()):
        col = colors[idx % len(colors)]
        distr = distribution[key]
        plt.figure()
        plt.hist(distr, bins=np.linspace(0.0, 1.0, 21), range=(0, 1), density=True, color=col)
        avg = np.mean(distr)
        std = np.std(distr)
        plt.axvline(avg, linestyle='-', color='black')
        plt.axvline(avg - std, linestyle='--', color='black')
        plt.axvline(avg + std, linestyle='--', color='black')
        plt.title('Histogram of vote share, avg={}, std={}'.format(round(avg, 2), round(std, 2)))
        plt.xlabel('fraction of votes')
        plt.ylabel('probability')
        plt.savefig(output_dir + name + '_' + str(key) + suffix + '.pdf')
        idx += 1


def plot_traj(traj, suffix, output_dir='plots/'):
    os.makedirs(output_dir, exist_ok=True)
    plt.figure()
    plt.plot(traj)
    plt.ylim(0, 1)
    plt.savefig(output_dir + '/traj' + suffix + '.pdf')


def save_data(config, results, suffix, output_dir='results/'):
    os.makedirs(output_dir, exist_ok=True)
    result = {'settings': vars(config.cmd_args),
              'results': prepare_json(results)}
    fname = output_dir + 'results' + suffix + '.json'
    with open(fname, 'w') as out_file:
        json.dump(result, out_file, indent=3)


def convert_to_distributions(series, missing_value=0):
    """
    Converts a list of dicts into a dict of lists
    :param series: a list of dicts
    :param missing_value: value to insert if a key in a series
    :result: a dict of lists
    """
    # Compute all keys that occur in the series
    keys = set()
    for d in series:
        keys.update(d.keys())
    res = {k: [d[k] for d in series] for k in keys}
    return res


def prepare_json(d):
    if isinstance(d, dict) or isinstance(d, Counter):
        res = {}
        for k, v in d.items():
            if isinstance(k, numbers.Integral):
                res[str(k)] = prepare_json(v)
            else:
                res[k] = prepare_json(v)
        return res
    if isinstance(d, Iterable):
        return [prepare_json(i) for i in d]
    return d


def run_experiment(config, N, q, EPS, SAMPLE_SIZE, THERM_TIME, n_zealots, ratio, **kwargs):
    # AFFINITY = [[0.2, 0.2], [0.2, 0.2]]  # change to get different network from SBM
    AFFINITY = planted_affinity(q, 5, np.ones(q) / q, ratio, N)  # all districts the same size and density

    suffix = config.suffix

    init_g = init_sbm(N, AFFINITY, state_generator=config.initialize_states)
    init_g = add_zealots(init_g, n_zealots, **config.zealots_config)

    g, traj = run_thermalization(config, init_g, EPS, THERM_TIME, each=100, n=N)
    plot_traj(traj, suffix)

    results = {system: [] for system in config.voting_systems.keys()}

    for i in range(SAMPLE_SIZE):
        print(i)
        if config.reset:
            g.vs()["state"] = config.initialize_states(N)
        g = run_symulation(config, g, EPS, N * 50, n=N)

        for system, fun in config.voting_systems.items():
            outcome = fun(g.vs)['fractions']
            results[system].append(outcome)

    for system in config.voting_systems.keys():
        distr = convert_to_distributions(results[system])
        plot_hist(distr, system, suffix)

    save_data(config, results, suffix)


def main():
    """
    Uses the command line parser from the config.parse module to obtain
    the relevant arguments to run the experiments. These are passed to the
    run_experiment function.
    """
    cfg = get_arguments()
    args_dict = vars(cfg.cmd_args)
    print('Running an experiment for the following settings:')
    print(args_dict)
    print('See other configuration options by running:', sys.argv[0], '--help')
    run_experiment(cfg, **args_dict)


if __name__ == '__main__':
    main()
