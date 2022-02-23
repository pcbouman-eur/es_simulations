# -*- coding: utf-8 -*-
import numpy as np
import sys

from tools import convert_to_distributions, save_data, read_data, run_with_time, calculate_indexes, compute_edge_ratio
from plotting import plot_indexes, plot_hist, plot_traj
from configuration.parser import get_arguments
from configuration.logging import log
from net_generation.base import init_graph, add_zealots
from simulation.base import run_simulation, run_thermalization, run_thermalization_simple


def run_experiment(n=None, epsilon=None, sample_size=None, therm_time=None, n_zealots=None, config=None, silent=True):
    """
    The main function for running the whole simulation - it generates the network,
    runs the voting process, and performs the elections. At the end results are saved in a json file.
    :param n: the number of nodes
    :param epsilon: the noise parameter
    :param sample_size: the number of repetitions of elections
    :param therm_time: the thermalization time
    :param n_zealots: the number of zealots
    :param config: the configuration class
    :param silent: whether to keep it silent and not print the sample number
    :return: None
    """
    init_g = init_graph(n, config.district_sizes, config.avg_deg, block_coords=config.district_coords,
                        ratio=config.ratio, planar_const=config.planar_c, euclidean=config.euclidean,
                        state_generator=config.initialize_states, random_dist=config.random_dist,
                        initial_state=config.not_zealot_state, all_states=config.all_states)
    init_g = add_zealots(init_g, n_zealots, zealot_state=config.zealot_state, **config.zealots_config)

    if not silent:
        link_fraction, link_ratio = compute_edge_ratio(init_g)
        log.info('There is ' + str(round(100.0 * link_fraction, 1)) + '% of inter-district connections')
        log.info('Ratio of inter- to intra-district links is equal ' + str(round(link_ratio, 3)))

    log.info(f"Running thermalization for {therm_time} time steps")
    if not silent:
        g, trajectory = run_thermalization(config, init_g, epsilon, therm_time, n=n)
        plot_traj(trajectory, config.suffix)
    else:
        g = run_thermalization_simple(config, init_g, epsilon, therm_time, n=n)

    results = {system: [] for system in config.voting_systems.keys()}

    for i in range(sample_size):
        if not silent:
            log.info(f"Computing sample no. {i}")

        if config.reset:
            g.vs()["state"] = config.initialize_states(n, all_states=config.all_states, state=config.not_zealot_state)
            # we have to reset zealots, otherwise they would have states different than 'zealot_state'
            g.vs()["zealot"] = np.zeros(n)
            g = add_zealots(g, n_zealots, zealot_state=config.zealot_state, **config.zealots_config)
            g = run_thermalization_simple(config, g, epsilon, therm_time, n=n)

        g = run_simulation(config, g, epsilon, n * config.mc_steps, n=n)

        for system, _function in config.voting_systems.items():
            outcome = _function(g.vs, states=config.all_states, total_seats=config.total_seats,
                                seats_per_district=config.seats_per_district, threshold=config.threshold,
                                assignment_func=config.seat_alloc_function)
            results[system].append(outcome['fractions'])

    save_data(config, results, config.suffix)


@run_with_time
def main(silent=False):
    """
    Uses the command line parser from the config.parse module to obtain
    the relevant arguments to run the experiments. These are passed to the
    run_experiment function.
    """
    cfg = get_arguments()
    log.info('Running simulation for the following configuration:')
    for key, value in cfg._cmd_args.items():
        log.info(' = '.join([key, str(value)]))
    log.info(f"See other configuration options by running: python {sys.argv[0].split('/')[-1]} --help")

    run_experiment(n=cfg.n, epsilon=cfg.epsilon, sample_size=cfg.sample_size, therm_time=cfg.therm_time,
                   n_zealots=cfg.n_zealots, config=cfg, silent=silent)

    # plot the results
    if not silent:  # to avoid plotting huge number of plots when using scripts
        res, _ = read_data(cfg.suffix)
        voting_distribution = convert_to_distributions(res['population'])
        for system in cfg.voting_systems.keys():
            distribution = convert_to_distributions(res[system])
            plot_hist(distribution, system, cfg.suffix, bins_num=cfg.q+2)
            indexes = calculate_indexes(voting_distribution, distribution, cfg.sample_size)
            plot_indexes(indexes, system, cfg.suffix)


if __name__ == '__main__':
    main()
