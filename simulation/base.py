# -*- coding: utf-8 -*-
"""
All the function necessary to run the dynamics of the simulation,
i.e. simulate the social/voting processes, mutate and propagate
states of the nodes etc.
"""
import random
import numpy as np
from collections import Counter
from electoral_sys.electoral_system import single_district_voting


###########################################################
#                                                         #
#               Mutation (random updates)                 #
#                                                         #
###########################################################

def default_mutation(node, all_states, p):
    """
    Default mutation mechanism that updates the state of a node whenever
    noise is applied.
    :param node: the node for which a new state is generated because of noise
    :param all_states: possible states of nodes
    :param p: probability of switching to state 'a' - mass media effect
    :result: the new mutated state for the node
    """
    k = len(all_states) - 1
    probs = [p] + [(1.0 - p) / k for _ in range(k)]
    return np.random.choice(all_states, p=probs)


###########################################################
#                                                         #
#              Propagation (social influence)             #
#                                                         #
###########################################################

def default_propagation(node, g):
    """
    Default propagation mechanism that selects a random neighbor
    and copies the state from the neighbor into the the target node
    as in the voter model.
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
    states amongst the neighbors, and selects a state that occurs the most often
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


###########################################################
#                                                         #
#                  The main algorithm                     #
#                                                         #
###########################################################

def run_simulation(config, g, noise_rate, steps, n=None):
    """
    Main algorithm of the simulation. Picks a node at random and performs
    state propagation or mutation according to model rules.
    :param config: a configuration object
    :param g: the igraph graph to run simulation on
    :param noise_rate: noise rate parameter of the model
    :param steps: the number of steps to perform in the simulation
    :param n: the size of the network
    :return: the graph object after changes
    """
    if n is None:
        n = len(g.vs())

    for _ in range(steps):
        node = np.random.randint(0, n)
        target = g.vs[node]
        if target["zealot"] == 0:
            rnum = random.random()
            if rnum > noise_rate:
                # Propagate
                target["state"] = config.propagate(target, g)
            else:
                # Mutate
                target["state"] = config.mutate(target, all_states=config.all_states, p=config.mass_media)

    return g


###########################################################
#                                                         #
#                Thermalization function                  #
#                                                         #
###########################################################

def run_thermalization(config, g, noise_rate, therm_time, each=1000, n=None):
    """
    A function running the simulation for a given number of steps
    and computing the trajectory.
    :param config: a configuration object
    :param g: the igraph graph to run simulation on
    :param noise_rate: noise rate parameter of the model
    :param therm_time: the number of steps to perform in thermalization
    :param each: integer, after how many steps to compute the trajectory point
    :param n: the size of the network
    :return: the graph object after changes, the trajectory
    """
    trajectory = {k: [v] for k, v in
                  single_district_voting(g.vs, states=config.all_states, total_seats=config.total_seats,
                                         assignment_func=config.seat_alloc_function)['vote_fractions'].items()}
    big_steps = round(therm_time / each)

    for t in range(big_steps):
        g = run_simulation(config, g, noise_rate, each, n=n)
        for key, value in single_district_voting(g.vs, states=config.all_states, total_seats=config.total_seats,
                                                 assignment_func=config.seat_alloc_function)['vote_fractions'].items():
            trajectory[key].append(value)

    return g, trajectory


def run_thermalization_simple(config, g, noise_rate, therm_time, n=None):
    """
    A simple version of the function <run_thermalization> that doesn't save the trajectory.
    :param config: a configuration object
    :param g: the igraph graph to run simulation on
    :param noise_rate: noise rate parameter of the model
    :param therm_time: the number of steps to perform in thermalization
    :param n: the size of the network
    :return: the graph object after changes
    """
    g = run_simulation(config, g, noise_rate, therm_time, n=n)
    return g
