import igraph as ig
import numpy as np
from matplotlib import pyplot as plt
from net_generation.base import init_sbm, add_zealots, planted_affinity
from simulation.base import run_symulation
from electoral_sys.electoral_system import system_population_majority, system_district_majority

N = 1000  # network size
q = 20
# AFFINITY = [[0.2, 0.01], [0.01, 0.2]]  # change to get different network from SBM
AFFINITY = planted_affinity(q, 5, np.ones(q) / q, 0.2, N)  # all districts the same size and density
EPS = 0.01  # noise rate


def plot_hist(distribution):
    plt.hist(distribution[1], bins=10, normed=True, color='green')
    plt.title('Histogram of vote share')
    plt.xlabel('fraction of votes')
    plt.ylabel('probability')
    plt.savefig('../../plot1.png')
    plt.show()

    plt.hist(distribution[-1], bins=10, normed=True, color='red')
    plt.title('Histogram of vote share')
    plt.xlabel('fraction of votes')
    plt.ylabel('probability')
    plt.savefig('../../plot2.png')
    plt.show()


def main():
    dist_population_wise = {1: [], -1: []}
    dist_district_wise = {1: [], -1: []}

    init_g = init_sbm(N, AFFINITY)
    init_g = add_zealots(init_g, 0)
    g = run_symulation(init_g, EPS, 200000, n=N)

    for i in range(1000):
        g = run_symulation(g, EPS, N*40, n=N)
        dist_population_wise[1].append(system_population_majority(g.vs)['fractions'][1])
        dist_population_wise[-1].append(system_population_majority(g.vs)['fractions'][-1])
        dist_district_wise[1].append(system_district_majority(g.vs)['fractions'][1])
        dist_district_wise[-1].append(system_district_majority(g.vs)['fractions'][-1])

    print(dist_population_wise)
    print(dist_district_wise)

    plot_hist(dist_population_wise)
    plot_hist(dist_district_wise)

    # just plotting graph
    # for i in range(N):
    #     if g.vs(i)["state"][0] == 1:
    #         g.vs(i)["color"] = 'green'
    # ig.plot(g)


if __name__ == '__main__':
    main()
