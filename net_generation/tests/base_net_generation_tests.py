# -*- coding: utf-8 -*-
import unittest
import numpy as np

from net_generation.base import default_initial_state, init_graph, planted_affinity, planar_affinity


class TestNetworkGeneration(unittest.TestCase):

    def test_default_initial_state(self):
        res = default_initial_state(2000, ('a', 'b', 'c'))
        self.assertEqual(len(res), 2000)
        self.assertSetEqual(set(res), {'a', 'b', 'c'})

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
        almost_correct_affinity = np.array([[0.25378, 0.02307, 0.02307],
                                            [0.02307, 0.25378, 0.01676],
                                            [0.02307, 0.01676, 0.25378]])
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


if __name__ == '__main__':
    unittest.main()
