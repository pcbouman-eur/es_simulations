import igraph as ig
import numpy as np


def planted_affinity(q, c, fractions, ratio, n):
    """

    :param q: number of districts
    :param c: average degree
    :param fractions: fractions of each district (numpy array with shape = (q,))
    :param ratio: ratio between density outside and inside of districts
    :param n: network size
    :return: list object with shape = (q, q).
    """
    p_in = c / (n * (ratio + (1.0 - ratio) * np.sum(fractions**2)))
    p_out = ratio * p_in
    p = p_out * np.ones(q) + (p_in - p_out) * np.eye(q)
    return p.tolist()


def init_sbm(n, affinity):
    """

    :param n: network size
    :param affinity: affinity matrix for SBM model
    :return: ig.Graph() object with...
    """
    q = len(affinity)
    block_sizes = np.repeat(n / q, q).tolist()
    g = ig.Graph.SBM(n, affinity, block_sizes)
    g.vs()["state"] = np.random.randint(0, 2, n) * 2 - 1

    g.vs()["zealot"] = np.zeros(n)  # you can add zealots as you wish
    
    group = np.zeros(n, dtype='int')
    for i in range(q - 1):
        group[int(np.sum(block_sizes[:(i + 1)])):] = i + 1
    g.vs['district'] = group
    return g


def add_zealots(g, m, one_district=False, district=None, degree_driven = False):
    """
    Function creating zealots in the network.
    Overwrite as you wish.
    :param g: ig.Graph() object
    :param m: number of zealots
    :param one_district: boolean, whether to add them to one district or randomly
    :param district: if one_district==True, which district to choose? In 'None', district is chosen randomly
    :return: ig.Graph() object
    """
    if one_district:
        if district is None:
            district = np.random.randint(np.max(g.vs['district']) + 1)
        ids = np.random.choice(np.where(np.array(g.vs['district']) == district)[0], replace = False, size=m)
    elif degree_driven:
        degrees = g.degree()
        degprob = degrees/np.sum(degrees)
        ids = np.random.choice(g.vcount(), size = m, replace = False, p = degprob)
    else:
        ids = np.random.randint(g.vcount(), replace = False, size=m)
    if len(ids):
        g.vs[list(ids)]['zealot'] = 1
        g.vs[list(ids)]['state'] = 1
    return g


if __name__ == '__main__':
    p = [[0.2, 0.01], [0.01, 0.2]]
    m = 100
    test_graph = init_sbm(m, p)
    colors = np.array(['blue', 'green'])
    test_graph.vs['color'] = colors[np.array(test_graph.vs['district']) - 1]
    ig.plot(test_graph)
