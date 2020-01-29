import igraph as ig
from matplotlib import pyplot as plt
from net_generation.base import init_sbm, add_zealots
from simulation.base import run_symulation
from electoral_sys.electoral_system import system_population_majority, system_district_majority

N = 500  # network size
AFFINITY = [[0.2, 0.01], [0.01, 0.2]]  # change to get different network from SBM
EPS = 0.01  # noise rate


def plot_hist(distribution):
    plt.hist(distribution, bins=10, normed=True)
    plt.title('Histogram of vote share')
    plt.xlabel('fraction of votes')
    plt.ylabel('probability')
    plt.show()


if __name__ == '__main__':
    dist_population_wise = {1: [], -1: []}
    dist_district_wise = {1: [], -1: []}

    init_g = init_sbm(N, AFFINITY)
    init_g = add_zealots(init_g)
    g = run_symulation(init_g, EPS, 100000, n=N)

    for i in range(500):
        g = run_symulation(g, EPS, N*10, n=N)
        dist_population_wise[1].append(system_population_majority(g.vs)['fractions'][1])
        dist_population_wise[-1].append(system_population_majority(g.vs)['fractions'][-1])
        dist_district_wise[1].append(system_district_majority(g.vs)['fractions'][1])
        dist_district_wise[-1].append(system_district_majority(g.vs)['fractions'][-1])

    print(dist_population_wise)
    print(dist_district_wise)

    plot_hist(dist_population_wise[1])
    plot_hist(dist_population_wise[-1])
    plot_hist(dist_district_wise[1])
    plot_hist(dist_district_wise[-1])

    # just plotting graph
    for i in range(N):
        if g.vs(i)["state"][0] == 1:
            g.vs(i)["color"] = 'green'
    ig.plot(g)
