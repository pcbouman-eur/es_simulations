# -*- coding: utf-8 -*-
"""
All the function necessary to generate networks for the simulation
"""
import igraph as ig
import numpy as np

from scipy.spatial.distance import squareform, pdist


###########################################################
#                                                         #
#                State initialization                     #
#                                                         #
###########################################################

def default_initial_state(n, all_states, **kwargs):
    """
    Generates n default initial states with equal probabilities, drawn from all_states
    :param n: the number of states to generate
    :param all_states: possible states of nodes
    :return: a numpy array of n states
    """
    return np.random.choice(all_states, size=n)


def consensus_initial_state(n, all_states, state=None, **kwargs):
    """
    Generates n identical states to create a full consensus
    :param n: the number of states to generate
    :param all_states: possible states of nodes
    :param state: the initial state for every node
    :return: a numpy array of n states
    """
    if state is None:
        state = all_states[-1]
    return [state for _ in range(n)]


###########################################################
#                                                         #
#                Generating the network                   #
#                                                         #
###########################################################

def planted_affinity(q, avg_deg, fractions, ratio, n):
    """
    Generates a matrix of connection probabilities between different
    communities in the Stochastic Block Model model.
    :param q: number of districts (int)
    :param avg_deg: average degree (float)
    :param fractions: fractions of each district (numpy array with shape = (q,))
    :param ratio: ratio between density outside and inside of districts (float)
    :param n: network size (int)
    :return: list object with shape = (q, q).
    """
    p_in = avg_deg / (n * (ratio + (1.0 - ratio) * np.sum(fractions ** 2)))
    p_out = ratio * p_in
    p = p_out * np.ones(q) + (p_in - p_out) * np.eye(q)
    return p.tolist()


def planar_affinity(avg_deg, fractions, coordinates, p_norm, c, n):
    """
    Generates a matrix of connection probabilities between different
    districts, based on their coordinates.
    :param avg_deg: average degree (float)
    :param fractions: fractions of each district (numpy array with shape = (q,))
    :param coordinates: the coordinates of the districts (numpy array with shape = (q, 2))
    :param p_norm: p-norm used for the distance metric in the planar network (float)
    :param c: constant in the function describing link probability for planar graph generator (float)
    :param n: network size (int)
    :return: list object with shape = (q, q).
    """
    dist_array = pdist(coordinates, 'minkowski', p=p_norm)
    dist_matrix = squareform(dist_array)

    affinity_matrix = 1.0 / (dist_matrix + c)

    norm_deg = n * affinity_matrix.dot(fractions).dot(fractions)
    affinity_matrix *= avg_deg / norm_deg
    return affinity_matrix.tolist()


def init_graph(n, block_sizes, block_coords, avg_deg, ratio, p_norm, planar_const,
               state_generator=default_initial_state, random_dist=False, initial_state=None, all_states=None):
    """
    Generates initial graph for simulations based on the Stochastic Block Model.
    :param n: network size (int)
    :param block_sizes: sizes of topological communities (list of ints)
    :param block_coords: the coordinates of the districts (list of lists)
    :param avg_deg: the average degree in the network (float)
    :param ratio: the ratio between density outside and inside of districts (float)
    :param p_norm: p-norm used for the distance metric in the planar network (float)
    :param planar_const: constant in the function describing link probability for planar graph generator (float)
    :param state_generator: function that generates the states
    :param random_dist: whether districts should be random (otherwise the same as communities) (bool)
    :param initial_state: initial state for the nodes used in the consensus initialization
    :param all_states: possible states of nodes
    :return: network with states, zealots, districts etc. (ig.Graph())
    """
    q = len(block_sizes)
    if block_coords is not None:
        affinity = planar_affinity(avg_deg, np.array(block_sizes) / n, np.array(block_coords), p_norm, planar_const, n)
    else:
        affinity = planted_affinity(q, avg_deg, np.array(block_sizes) / n, ratio, n)

    g = ig.Graph.SBM(n, affinity, block_sizes)

    g.vs()["state"] = state_generator(n, all_states=all_states, state=initial_state)
    g.vs()["zealot"] = np.zeros(n)  # you can add zealots as you wish

    group = np.zeros(n, dtype='int')
    for i in range(q - 1):
        group[int(np.sum(block_sizes[:(i + 1)])):] = i + 1
    if not random_dist:
        g.vs['district'] = group
    else:
        g.vs['district'] = np.random.permutation(group)
    return g


###########################################################
#                                                         #
#                  Defining zealots                       #
#                                                         #
###########################################################

def add_zealots(g, m, one_district=False, district=None, degree_driven=False, zealot_state='a'):
    """
    Function creating zealots in the network.
    Overwrite as you wish.
    :param g: ig.Graph() object
    :param m: number of zealots
    :param one_district: boolean, whether to add them to one district or randomly
    :param district: if one_district==True, which district to choose? If 'None', district is chosen randomly
    :param degree_driven: if True choose nodes proportionally to the degree
    :param zealot_state: state to assign for zealots
    :return: ig.Graph() object
    """
    if one_district:
        if district is None:
            district = np.random.randint(np.max(g.vs['district']) + 1)
        ids = np.random.choice(np.where(np.array(g.vs['district']) == district)[0], replace=False, size=m)
    elif degree_driven:
        degrees = g.degree()
        deg_prob = degrees / np.sum(degrees)
        ids = np.random.choice(g.vcount(), size=m, replace=False, p=deg_prob)
    else:
        ids = np.random.choice(g.vcount(), size=m, replace=False)
    if len(ids):
        # apparently igraph can understand only python integers as node ids,
        # list comprehension below is not the most optimal way to obtain a list of python integers,
        # but using numpy key-word argument 'dtype' or the method 'astype' with type 'int'
        # still returns arrays with entries as 'numpy.int64' instead of python 'int'
        zealots = [int(_id) for _id in ids]
        g.vs[zealots]['zealot'] = 1
        g.vs[zealots]['state'] = zealot_state
    return g
