# -*- coding: utf-8 -*-
import numpy as np
import sys

from tools import convert_to_distributions, save_data, read_data, run_with_time, calculate_indexes
from tools import plot_indexes, plot_hist, plot_traj
from configuration.parser import get_arguments
from configuration.logging import log
from net_generation.base import init_sbm, add_zealots, planted_affinity
from simulation.base import run_simulation, run_thermalization, run_thermalization_silent
from electoral_sys.electoral_system import electoral_threshold


def run_experiment(n=None, q=None, epsilon=None, sample_size=None, therm_time=None, n_zealots=None, ratio=None,
                   avg_deg=None, config=None):
    affinity = planted_affinity(q, avg_deg, np.ones(q) / q, ratio, n)  # all districts the same size and density

    suffix = config.suffix

    init_g = init_sbm(n, affinity, state_generator=config.initialize_states, random_dist=config.random_dist,
                      initial_state=config.not_zealot_state, all_states=config.all_states)
    init_g = add_zealots(init_g, n_zealots, zealot_state=config.zealot_state, **config.zealots_config)

    g, traj = run_thermalization(config, init_g, epsilon, therm_time, each=100, n=n)
    plot_traj(traj, suffix)

    results = {system: [] for system in config.voting_systems.keys()}

    for i in range(sample_size):
        log.info(f"Computing sample no. {i}")

        if config.reset:
            g.vs()["state"] = config.initialize_states(n, all_states=config.all_states, state=config.not_zealot_state)
            # we have to reset zealots, otherwise they would have states different than 'zealot_state'
            g.vs()["zealot"] = np.zeros(n)
            g = add_zealots(g, n_zealots, zealot_state=config.zealot_state, **config.zealots_config)
            g = run_thermalization_silent(config, g, epsilon, therm_time, n=n)

        g = run_simulation(config, g, epsilon, n * config.mc_steps, n=n)

        for system, fun in config.voting_systems.items():
            # outcome = fun(electoral_threshold(g.vs, config.threshold), states=config.all_states)['fractions']
            outcome = fun(electoral_threshold(g.vs, config.threshold), states=config.all_states)
            results[system].append(outcome['fractions'])
            print(system, outcome['seats'])

    save_data(config, results, suffix)


@run_with_time
def main():
    """
    Uses the command line parser from the config.parse module to obtain
    the relevant arguments to run the experiments. These are passed to the
    run_experiment function.
    """
    cfg = get_arguments()
    log.info('Running an experiment for the following configuration:')
    for key, value in cfg._cmd_args.items():
        log.info(' = '.join([key, str(value)]))
    log.info(f"See other configuration options by running: python {sys.argv[0].split('/')[-1]} --help")

    run_experiment(n=cfg.n, q=cfg.q, epsilon=cfg.epsilon, sample_size=cfg.sample_size, therm_time=cfg.therm_time,
                   n_zealots=cfg.n_zealots, ratio=cfg.ratio, avg_deg=cfg.avg_deg, config=cfg)

    # plot the results
    res, _ = read_data(cfg.suffix)
    voting_distribution = convert_to_distributions(res['population'])
    for system in cfg.voting_systems.keys():
        distribution = convert_to_distributions(res[system])
        plot_hist(distribution, system, cfg.suffix, bins_num=cfg.q+1)
        indexes = calculate_indexes(voting_distribution, distribution, cfg.sample_size)
        plot_indexes(indexes, system, cfg.suffix)


if __name__ == '__main__':
    main()
