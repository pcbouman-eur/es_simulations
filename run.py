import igraph as ig
from net_generation.base import init_sbm
from simulation.base import run_symulation
from electoral_sys.electoral_system import system_population_majority, system_district_majority

N = 500
AFFINITY = [[0.2, 0.01], [0.01, 0.2]]
EPS = 0.01


if __name__ == '__main__':
    init_g = init_sbm(N, AFFINITY)
    g = run_symulation(init_g, EPS, 100000, n=N)

    print(system_population_majority(g.vs))
    print(system_district_majority(g.vs))  # TODO collect statistics

    # just plotting graph
    for i in range(N):
        if g.vs(i)["state"][0] == 1:
            g.vs(i)["color"] = 'green'
    ig.plot(g)
