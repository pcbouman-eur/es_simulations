import igraph as ig
import random
import numpy as np
from electoral_sys.electoral_system import system_population_majority

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


def run_thermalization(g, noise_rate, nrun, each, n=None):
        
    traj = [system_population_majority(g.vs)['fractions'][1]]
    
    for t in range(nrun):
        g = run_symulation(g, noise_rate, each)
        traj.append(system_population_majority(g.vs)['fractions'][1])
            
    return g, traj
