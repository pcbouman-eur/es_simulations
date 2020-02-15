import igraph as ig
import random
import numpy as np
from electoral_sys.electoral_system import system_population_majority



def default_mutation(node):
    """
    Default mutation mechanism that updates the state of a node whenever
    noise is applied. The default mechanism multiplies the state of the
    agent by -1

    :param node: the node for which a new state is generated because of noise
    :result: the new mutated state for the node
    """
    return node["state"] * -1


def default_propagation(node, g):
    """
    Default propagation mechanism that selects a random neighbor
    and copies the state from the neighbor into the the target node

    :param node: the node to which a new state can be propagated
    :param neighbours: the neighbors of the node
    :param g: the graph in which the node and neighbours live
    :result: the new state for the node
    """
    neighbours = g.neighbors(node)
    if neighbours:
        target_neighbor = random.sample(neighbours, 1)[0]
        return g.vs[target_neighbor]["state"]
    return node["state"]
    
    
def run_symulation(g, noise_rate, max_step, n=None, mutate=default_mutation,
                   propagate=default_propagation):
    if n is None:
        n = len(g.vs())
        
    for _ in range(max_step):
        node = np.random.randint(0, n)
        target = g.vs[node]
        if target["zealot"] == 0:
            rnum = random.random()
            if rnum <= noise_rate / 2.0:
                # Mutate
                target["state"] = mutate(target)
            elif rnum > noise_rate:
                # Propagate
                target["state"] = propagate(target, g)
    return g


def run_thermalization(g, noise_rate, therm_time, each, n=None):
        
    traj = [system_population_majority(g.vs)['fractions'][1]]
    nrun = round(therm_time/each)
    for t in range(nrun):
        g = run_symulation(g, noise_rate, each)
        traj.append(system_population_majority(g.vs)['fractions'][1])
            
    return g, traj
