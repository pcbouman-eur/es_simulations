import igraph as ig
import numpy as np


def planted_affinity(q, avg_deg, fractions, ratio, n):
    """

    :param q: number of districts
    :param avg_deg: average degree
    :param fractions: fractions of each district (numpy array with shape = (q,))
    :param ratio: ratio between density outside and inside of districts
    :param n: network size
    :return: list object with shape = (q, q).
    """
    p_in = avg_deg / (n * (ratio + (1.0 - ratio) * np.sum(fractions ** 2)))
    p_out = ratio * p_in
    p = p_out * np.ones(q) + (p_in - p_out) * np.eye(q)
    return p.tolist()


def default_initial_state(n):
    """
    Generates n default -1 or 1 initial states with equal probabilities
    :param n: the number of states to generate
    :return: a numpy array of n states
    """
    return np.random.randint(0, 2, n) * 2 - 1


def initial_state_abc(n):
    """
    Generates n initial states from values 'a', 'b', and 'c' with equal probabilities
    :param n: the number of states to generate
    :return: a numpy array of n states
    """
    return np.random.choice(['a', 'b', 'c'], size=n)


def init_sbm(n, affinity, state_generator=default_initial_state, districts_are_communities=True):
    """
    Generates initial graph for simulations
    :param n: network size (int)
    :param affinity: affinity matrix for SBM model (list())
    :param state_generator: function that generates the states
    :param districts_are_communities: whether districts and communities should be the same (bool)
    :return: network with states, zealots, districts etc. (ig.Graph())
    """
    q = len(affinity)
    block_sizes = np.repeat(n / q, q).tolist()
    g = ig.Graph.SBM(n, affinity, block_sizes)
    g.vs()["state"] = state_generator(n)

    g.vs()["zealot"] = np.zeros(n)  # you can add zealots as you wish

    group = np.zeros(n, dtype='int')
    for i in range(q - 1):
        group[int(np.sum(block_sizes[:(i + 1)])):] = i + 1
    if districts_are_communities:
        g.vs['district'] = group
    else:
        g.vs['district'] = np.random.permutation(group)
    return g


def add_zealots(g, m, one_district=False, district=None, degree_driven=False, zealot_state=1):
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


if __name__ == '__main__':
    p = [[0.2, 0.01], [0.01, 0.2]]
    m = 100
    test_graph = init_sbm(m, p)
    colors = np.array(['blue', 'green'])
    test_graph.vs['color'] = colors[np.array(test_graph.vs['district']) - 1]
    ig.plot(test_graph)
