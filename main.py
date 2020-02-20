# import igraph as ig
import numpy as np
import sys
import os
from matplotlib import pyplot as plt
from configuration.parser import get_arguments
from net_generation.base import init_sbm, add_zealots, planted_affinity
from simulation.base import run_symulation, run_thermalization
from electoral_sys.electoral_system import system_population_majority, system_district_majority

def plot_hist(distribution, name1, name2, suffix, output_dir='plots/'):
    os.makedirs(output_dir, exist_ok=True)
    plt.figure()
    plt.hist(distribution[1], bins=np.linspace(0.0, 1.0, 21), range=(0, 1), density=True, color='green')
    avg = np.mean(distribution[1])
    std = np.std(distribution[1])
    plt.axvline(avg, linestyle='-', color='black')
    plt.axvline(avg - std, linestyle='--', color='black')
    plt.axvline(avg + std, linestyle='--', color='black')
    plt.title('Histogram of vote share, avg={}, std={}'.format(round(avg, 2), round(std, 2)))
    plt.xlabel('fraction of votes')
    plt.ylabel('probability')
    plt.savefig(output_dir + name1 + '' + suffix + '.pdf')

    plt.figure()
    plt.hist(distribution[-1], bins=np.linspace(0.0, 1.0, 21), range=(0, 1), density=True, color='red')
    avg = np.mean(distribution[-1])
    std = np.std(distribution[-1])
    plt.axvline(avg, linestyle='-', color='black')
    plt.axvline(avg - std, linestyle='--', color='black')
    plt.axvline(avg + std, linestyle='--', color='black')
    plt.title('Histogram of vote share, avg={}, std={}'.format(round(avg, 2), round(std, 2)))
    plt.xlabel('fraction of votes')
    plt.ylabel('probability')
    plt.savefig(output_dir + name2 + '' + suffix + '.pdf')


def plot_traj(traj, suffix, output_dir='plots/'):
    os.makedirs(output_dir, exist_ok=True)
    plt.figure()
    plt.plot(traj)
    plt.ylim(0, 1)
    plt.savefig(output_dir+'/traj' + suffix + '.pdf')


def run_experiment(config, N, q, EPS, SAMPLE_SIZE, THERM_TIME, n_zealots, ratio, **kwargs):
    # AFFINITY = [[0.2, 0.2], [0.2, 0.2]]  # change to get different network from SBM
    AFFINITY = planted_affinity(q, 5, np.ones(q) / q, ratio, N)  # all districts the same size and density

    suffix = config.suffix
    #'_N_' + str(N) + '_q_' + str(q) + '_EPS_' + str(EPS) + '_S_' + str(SAMPLE_SIZE) + '_T_' + str(THERM_TIME) + '_R_' + str(ratio)

    # dist_population_wise = {1: [], -1: []}
    # dist_district_wise = {1: [], -1: []}

    init_g = init_sbm(N, AFFINITY, state_generator=config.initial_states)
    init_g = add_zealots(init_g, n_zealots, **config.zealots_config)
    # for i in range(2):
    #     init_g = add_zealots(init_g, n_zealots, one_district=one_dist, district=i, degree_driven=degdriv)

    g, traj = run_thermalization(config, init_g, EPS, THERM_TIME, each=100, n=N)
    plot_traj(traj, suffix)

    # TODO: change to be more flexible for different state types as this assumes -1 and 1 states
    results = {system : {1 : [], -1: []} for system in config.voting_systems.keys()}

    for i in range(SAMPLE_SIZE):
        print(i)
        g = run_symulation(config, g, EPS, N*50, n=N)
        
        for system,fun in config.voting_systems.items():
            outcome = fun(g.vs)['fractions']
            results[system][1].append(outcome[1])
            results[system][-1].append(outcome[-1])

        # population = system_population_majority(g.vs)['fractions']
        # dist_population_wise[1].append(population[1])
        # dist_population_wise[-1].append(population[-1])

        # district = system_district_majority(g.vs)['fractions']
        # dist_district_wise[1].append(district[1])
        # dist_district_wise[-1].append(district[-1])

    for system in config.voting_systems.keys():
        plot_hist(results[system], system+'1', system+'-1', suffix)
    
    # plot_hist(dist_population_wise, 'population1', 'population-1', suffix)
    # plot_hist(dist_district_wise, 'district1', 'district-1', suffix)

    # just plotting graph
    # for i in range(N):
    #     if g.vs(i)["state"][0] == 1:
    #         g.vs(i)["color"] = 'green'
    # ig.plot(g)


def main():
    '''
    Uses the command line parser from the config.parse module to obtain
    the relevant arguments to run the experiments. These are passed to the
    run_experiment function.
    '''
    cfg = get_arguments()
    args_dict = vars(cfg.cmd_args)
    print('Running an experiment for the following settings:')
    print(args_dict)
    print('See other configuration options by running:', sys.argv[0], '--help')
    run_experiment(cfg, **args_dict)


if __name__ == '__main__':
    main()
