import igraph as ig
import numpy as np


def init_sbm(n, af_matrix):
    """

    :param n: network size
    :param af_matrix: affinity matrix for SBM model
    :return: ig.Graph() object with...
    """
    g = ig.Graph()
    g.vs()["state"] = np.random.randint(0, 2, n) * 2 - 1
