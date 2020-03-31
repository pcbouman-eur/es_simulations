import igraph as ig
import random
import numpy as np
from collections import Counter
from electoral_sys.electoral_system import system_population_majority


def default_mutation(node):
    """
    Default mutation mechanism that updates the state of a node whenever
    noise is applied. The default mechanism multiplies the state of the
    agent by -1
    :param node: the node for which a new state is generated because of noise
    :result: the new mutated state for the node
    """
    return np.random.choice([-1, 1])


def mutation_abc(node):
    """
    Mutation in the 3-satate model where states are 'a', 'b', 'c'
    :param node: the node for which a new state is generated because of noise
    :result: the new mutated state for the node
    """
    return np.random.choice(['a', 'b', 'c'])


def default_propagation(node, g):
    """
    Default propagation mechanism that selects a random neighbor
    and copies the state from the neighbor into the the target node

    :param node: the node to which a new state can be propagated
    :param g: the graph in which the node and neighbours live
    :result: the new state for the node
    """
    neighbours = g.neighbors(node)
    if neighbours:
        target_neighbor = random.sample(neighbours, 1)[0]
        return g.vs[target_neighbor]["state"]
    return node["state"]


def majority_propagation(node, g, inverse=False):
    """
    Majority propagation mechanism that looks at the distribution of
    states amongst the neigbors, and selects a state that occurs the most
    often
    
    :param node: the node to which a new state will be propagated
    :param g: the igraph graph where the node and neighbours live
    :param inverse: if propagation should be done from the minority instead
    :result: the new state for the node
    """
    neighbours = g.neighbors(node)
    if neighbours:
        c = Counter([g.vs[n]["state"] for n in neighbours])
        counts = c.most_common()
        if inverse:
            max_count = counts[-1][1]
        else:
            max_count = counts[0][1]
        selection = [state for state, count in counts if count == max_count]
        if len(selection) == 1:
            return selection[0]
        return random.sample(selection, 1)[0]
    return node["state"]


def run_simulation(config, g, noise_rate, max_step, n=None):
    if n is None:
        n = len(g.vs())

    for _ in range(max_step):
        node = np.random.randint(0, n)
        target = g.vs[node]
        if target["zealot"] == 0:
            rnum = random.random()
            if rnum > noise_rate:
                # Propagate
                target["state"] = config.propagate(target, g)
            else:
                # Mutate
                target["state"] = config.mutate(target)

    return g


def run_thermalization(config, g, noise_rate, therm_time, each, n=None):
    traj = {k: [v] for k, v in system_population_majority(g.vs)['fractions'].items()}
    nrun = round(therm_time / each)

    for t in range(nrun):
        g = run_simulation(config, g, noise_rate, each)
        for key, value in system_population_majority(g.vs)['fractions'].items():
            traj[key].append(value)

    return g, traj
