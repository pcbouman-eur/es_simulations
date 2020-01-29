import igraph as ig
import random
import numpy as np


def run_symulation(g, noise_rate, max_step, n=None):
    if n is None:
        n = len(g.vs())

    for t in range(max_step):
        node = np.random.randint(0, n)
        if g.vs[node]["zealot"] == 0:
            rnum = random.random()
            if rnum <= noise_rate / 2.0:
                g.vs[node]["state"] *= -1
            elif rnum > noise_rate:
                neighbours = g.neighbors(node)
                if neighbours:
                    target_neighbor = random.sample(neighbours, 1)[0]
                    g.vs[node]["state"] = g.vs[target_neighbor]["state"]

    return g
