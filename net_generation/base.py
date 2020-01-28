import igraph as ig
import numpy as np


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

    group = np.zeros(n, dtype='int')
    for i in range(q - 1):
        group[int(np.sum(block_sizes[:(i + 1)])):] = i + 1
    g.vs['district'] = group
    return g


if __name__ == '__main__':
    affinity = [[0.2, 0.01], [0.01, 0.2]]
    g = init_sbm(100, affinity)
    colors = np.array(['blue', 'green'])
    g.vs['color'] = colors[np.array(g.vs['district']) - 1]
    ig.plot(g)