import igraph as ig
import numpy as np


def planted_affinity(q, c, fractions, eps, n):
    """

    :param q: number of districts
    :param c: average degree
    :param fractions: fractions of each district (numpy array with shape = (q,))
    :param eps: ratio between density outside and inside of districts
    :param n: network size
    :return: np.array() object with shape = (q, q).
    """
    p_in = c / (n * (eps + (1.0 - eps) * np.sum(fractions**2)))
    p_out = eps * p_in
    p = p_out * np.ones(q) + (p_in - p_out) * np.eye(q)
    return p


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


def add_zealots(g):
    """
    Function creating zealots in the network.
    Overwrite as you wish.
    :param g: ig.Graph() object
    :return: ig.Graph() object
    """
    # g.vs(10)['zealot'] = 1  # this will make node no. 10 a zealot
    return g


if __name__ == '__main__':
    p = [[0.2, 0.01], [0.01, 0.2]]
    m = 100
    test_graph = init_sbm(m, p)
    colors = np.array(['blue', 'green'])
    test_graph.vs['color'] = colors[np.array(test_graph.vs['district']) - 1]
    ig.plot(test_graph)
