import igraph as ig
import numpy as np
import sys
from matplotlib import pyplot as plt
from net_generation.base import init_sbm, add_zealots, planted_affinity
from simulation.base import run_symulation, run_thermalization
from electoral_sys.electoral_system import system_population_majority, system_district_majority

if len(sys.argv) == 1 :
    N = 1000
    q = 20
    EPS = 0.01
    SAMPLE_SIZE = 500
    THERM_TIME = 10000
else :
    N = int(sys.argv[1]) #size of the network
    q = int(sys.argv[2]) #number of districts
    EPS = float(sys.argv[3])  # noise rate
    SAMPLE_SIZE = int(sys.argv[4]) # number of points
    THERM_TIME = int(sys.argv[5])  # thermalization time steps

# AFFINITY = [[0.2, 0.2], [0.2, 0.2]]  # change to get different network from SBM
AFFINITY = planted_affinity(q, 5, np.ones(q) / q, 0.2, N)  # all districts the same size and density

sufix = '_N_' + str(N) + '_q_' + str(q) + '_EPS_' + str(EPS) + '_S_' + str(SAMPLE_SIZE) + '_T_' + str(THERM_TIME)


def plot_hist(distribution, name1, name2):
    plt.figure()
    plt.hist(distribution[1], bins=np.linspace(0.0, 1.0, 40), range=(0, 1), density=True, color='green')
    avg = np.mean(distribution[1])
    std = np.std(distribution[1])
    plt.axvline(avg, linestyle='-', color='black')
    plt.axvline(avg - std, linestyle='--', color='black')
    plt.axvline(avg + std, linestyle='--', color='black')
    plt.title('Histogram of vote share, avg={}, std={}'.format(round(avg, 2), round(std, 2)))
    plt.xlabel('fraction of votes')
    plt.ylabel('probability')
    plt.savefig(name1 + '' + sufix + '.pdf')

    plt.figure()
    plt.hist(distribution[-1], bins=np.linspace(0.0, 1.0, 40), range=(0, 1), density=True, color='red')
    avg = np.mean(distribution[-1])
    std = np.std(distribution[-1])
    plt.axvline(avg, linestyle='-', color='black')
    plt.axvline(avg - std, linestyle='--', color='black')
    plt.axvline(avg + std, linestyle='--', color='black')
    plt.title('Histogram of vote share, avg={}, std={}'.format(round(avg, 2), round(std, 2)))
    plt.xlabel('fraction of votes')
    plt.ylabel('probability')
    plt.savefig(name2 + '' + sufix + '.pdf')


def plot_traj(traj):
    plt.figure()
    plt.plot(traj)
    plt.ylim(0,1)
    plt.savefig('traj' + sufix + '.pdf')


def main():
    dist_population_wise = {1: [], -1: []}
    dist_district_wise = {1: [], -1: []}

    init_g = init_sbm(N, AFFINITY)
    init_g = add_zealots(init_g, 0)

    g, traj = run_thermalization(init_g, EPS, THERM_TIME, each=100, n=N)
    plot_traj(traj)

    for i in range(SAMPLE_SIZE):
        print(i)
        g = run_symulation(g, EPS, N*50, n=N)
        population = system_population_majority(g.vs)['fractions']
        dist_population_wise[1].append(population[1])
        dist_population_wise[-1].append(population[-1])

        district = system_district_majority(g.vs)['fractions']
        dist_district_wise[1].append(district[1])
        dist_district_wise[-1].append(district[-1])

    plot_hist(dist_population_wise, 'population1', 'population-1')
    plot_hist(dist_district_wise, 'district1', 'district-1')

    # just plotting graph
    # for i in range(N):
    #     if g.vs(i)["state"][0] == 1:
    #         g.vs(i)["color"] = 'green'
    # ig.plot(g)


if __name__ == '__main__':
    main()
