# -*- coding: utf-8 -*-
import unittest
import numpy as np
import igraph as ig
from collections import Counter

from net_generation.base import default_initial_state, consensus_initial_state, add_zealots
from net_generation.base import init_graph, planted_affinity, planar_affinity


class TestNetworkGeneration(unittest.TestCase):

    def test_default_initial_state(self):
        res = default_initial_state(2000, ('a', 'b', 'c'))
        self.assertEqual(len(res), 2000)
        self.assertSetEqual(set(res), {'a', 'b', 'c'})

    def test_consensus_initial_state(self):
        res = consensus_initial_state(1000, ('a', 'b', 'c'), state='b')
        self.assertEqual(res, ['b' for _ in range(1000)])

    def test_consensus_initial_state_no_state(self):
        res = consensus_initial_state(9999, ('a', 'b', 'c', 'd'))
        self.assertEqual(res, ['d' for _ in range(9999)])

    def test_planted_affinity(self):
        n = 100
        q = 2
        fractions = np.array([0.6, 0.4])
        avg = 10
        ratio = 0.05

        affinity = planted_affinity(q, avg, fractions, ratio, n)
        almost_correct_affinity = np.array([[0.18382, 0.00919], [0.00919, 0.18382]])
        np.testing.assert_array_almost_equal(affinity, almost_correct_affinity, decimal=5)

    def test_euclidean_planar_affinity(self):
        n = 100
        fractions = np.array([0.3, 0.4, 0.3])
        coordinates = [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]
        avg = 10
        c = 0.1

        affinity = planar_affinity(avg, fractions, coordinates, c, n, euclidean=True)
        almost_correct_affinity = np.array([[0.29026, 0.0024, 0.0024],
                                            [0.0024, 0.29026, 0.00127],
                                            [0.0024, 0.00127, 0.29026]])
        np.testing.assert_array_almost_equal(affinity, almost_correct_affinity, decimal=5)

    def test_sbm_avg_deg(self):
        n = 1000
        avg_deg = 10.0
        graph = init_graph(n, [600, 400], avg_deg, block_coords=None, ratio=0.05, planar_const=100.0,
                           all_states=['a', 'b'])
        self.assertAlmostEqual(avg_deg, np.mean(graph.degree()), places=0)

    def test_sbm_avg_deg_no_ratio(self):
        n = 1000
        avg_deg = 10.0

        def test_func():
            init_graph(n, [600, 400], avg_deg, block_coords=None, ratio=None, all_states=['a', 'b'])
        self.assertRaises(TypeError, test_func)

    def test_planar_avg_deg(self):
        n = 1000
        avg_deg = 10.0
        graph = init_graph(n, [300, 400, 300], avg_deg, block_coords=[[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]], ratio=0.05,
                           planar_const=100.0, all_states=['a', 'b'])
        self.assertAlmostEqual(avg_deg, np.mean(graph.degree()), places=0)

    def test_planar_avg_deg_no_planar_c(self):
        n = 1000
        avg_deg = 10.0

        def test_func():
            init_graph(n, [300, 400, 300], avg_deg, block_coords=[[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]], ratio=0.05,
                       all_states=['a', 'b'])
        self.assertRaises(TypeError, test_func)

    def test_init_graph_node_attributes(self):
        n = 1300
        avg_deg = 10.0
        init_g = init_graph(n, [600, 400, 300], avg_deg, ratio=0.01, all_states=['a', 'b', 'd'])
        self.assertIsInstance(init_g, ig.Graph)
        self.assertSetEqual(set(init_g.vs['state']), {'a', 'b', 'd'})
        self.assertSetEqual(set(init_g.vs['zealot']), {0})
        self.assertListEqual(init_g.vs[0:600]['district'], [0 for _ in range(600)])
        self.assertListEqual(init_g.vs[600:1000]['district'], [1 for _ in range(400)])
        self.assertListEqual(init_g.vs[1000:1300]['district'], [2 for _ in range(300)])

    def test_add_zealots_random(self):
        g = ig.Graph(20)
        g.vs['state'] = 'c'
        g.vs['zealot'] = 0
        g = add_zealots(g, 15, 'a')
        self.assertDictEqual(Counter(g.vs['state']), {'a': 15, 'c': 5})
        self.assertDictEqual(Counter(g.vs['zealot']), {1: 15, 0: 5})

    def test_add_zealots_one_dist(self):
        g = ig.Graph(30)
        g.vs['state'] = 'b'
        g.vs['zealot'] = 0
        g.vs[0:6]['district'] = 0
        g.vs[6:11]['district'] = 1
        g.vs[11:30]['district'] = 2
        g = add_zealots(g, 3, 'c', one_district=True, district=1)
        self.assertDictEqual(Counter(g.vs[6:11]['state']), {'b': 2, 'c': 3})
        self.assertDictEqual(Counter(g.vs[6:11]['zealot']), {1: 3, 0: 2})
        self.assertDictEqual(Counter(g.vs['state']), {'b': 27, 'c': 3})
        self.assertDictEqual(Counter(g.vs['zealot']), {1: 3, 0: 27})


if __name__ == '__main__':
    unittest.main()
