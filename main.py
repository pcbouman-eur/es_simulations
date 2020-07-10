# -*- coding: utf-8 -*-
import numpy as np
import sys
import os
import json
from matplotlib import pyplot as plt
from tools import convert_to_distributions, prepare_json
from configuration.parser import get_arguments
from net_generation.base import init_sbm, add_zealots, planted_affinity
from simulation.base import run_simulation, run_thermalization, run_thermalization_silent
from electoral_sys.electoral_system import electoral_threshold


def plot_hist(distribution, name, suffix, output_dir='plots/', colors=('tomato', 'mediumseagreen', 'cornflowerblue')):
    os.makedirs(output_dir, exist_ok=True)

    for idx, key in enumerate(sorted(distribution.keys())):
        col = colors[idx % len(colors)]
        distr = distribution[key]

        plt.figure(figsize=(4, 3))
        plt.hist(distr, bins=np.linspace(0.0, 1.0, 21), range=(0, 1), density=True, color=col)

        avg = np.mean(distr)
        std = np.std(distr)
        plt.axvline(avg, linestyle='-', color='black')
        plt.axvline(avg - std, linestyle='--', color='black')
        plt.axvline(avg + std, linestyle='--', color='black')

        plt.title('Histogram of vote share, avg={}, std={}'.format(round(avg, 2), round(std, 2)))
        plt.xlabel('fraction of votes')
        plt.ylabel('probability')

        plt.tight_layout()
        plt.savefig(output_dir + name + '_' + str(key) + suffix + '.pdf')


def plot_traj(traj, suffix, output_dir='plots/', colors=('tomato', 'mediumseagreen', 'cornflowerblue')):
    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(4, 3))

    for i, key in enumerate(sorted(traj.keys())):
        plt.plot(traj[key], color=colors[i % len(colors)], label=str(key))

    plt.ylim(0, 1)
    plt.legend()

    plt.xlabel('time steps [in hundreds]')
    plt.ylabel('fraction of N')
    plt.title('Trajectory during thermalization')

    plt.tight_layout()
    plt.savefig('{}/trajectory{}.pdf'.format(output_dir, suffix))


def save_data(config, results, suffix, output_dir='results/'):
    os.makedirs(output_dir, exist_ok=True)
    result = {'settings': vars(config.cmd_args),
              'results': prepare_json(results)}
    fname = output_dir + 'results' + suffix + '.json'
    with open(fname, 'w') as out_file:
        json.dump(result, out_file, indent=3)


def run_experiment(config, N, q, EPS, SAMPLE_SIZE, THERM_TIME, n_zealots, ratio, avg_deg, **kwargs):
    # AFFINITY = [[0.2, 0.2], [0.2, 0.2]]  # change to get different network from SBM
    AFFINITY = planted_affinity(q, avg_deg, np.ones(q) / q, ratio, N)  # all districts the same size and density

    suffix = config.suffix

    init_g = init_sbm(N, AFFINITY, state_generator=config.initialize_states,
                      districts_are_communities=config.distr_eq_comm)
    init_g = add_zealots(init_g, n_zealots, zealot_state=config.zealot_state, **config.zealots_config)

    g, traj = run_thermalization(config, init_g, EPS, THERM_TIME, each=100, n=N)
    plot_traj(traj, suffix)

    results = {system: [] for system in config.voting_systems.keys()}

    for i in range(SAMPLE_SIZE):
        print(i)

        if config.reset:
            g.vs()["state"] = config.initialize_states(N)
            # we have to reset zealots, otherwise they would have states different than 'zealot_state'
            # TODO: maybe whole initialization of SBM should be repeated? for now seems not necessary
            g.vs()["zealot"] = np.zeros(N)
            g = add_zealots(g, n_zealots, zealot_state=config.zealot_state, **config.zealots_config)
            g = run_thermalization_silent(config, g, EPS, THERM_TIME, n=N)

        g = run_simulation(config, g, EPS, N * config.cmd_args.mc_steps, n=N)

        for system, fun in config.voting_systems.items():
            outcome = fun(electoral_threshold(g.vs, config.threshold))['fractions']
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
