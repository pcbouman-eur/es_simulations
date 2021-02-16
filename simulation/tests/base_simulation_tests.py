# -*- coding: utf-8 -*-
import unittest
import igraph as ig

from simulation.base import default_mutation


class TestSimulationBase(unittest.TestCase):

    def test_default_mutation_one(self):
        graph = ig.Graph.Full(3)
        res = default_mutation(graph.vs(1), ('a', 'b', 'c'), 1.0/3)
        self.assertIn(res, ('a', 'b', 'c'))

    def test_default_mutation_two(self):
        graph = ig.Graph.Full(3)
        res = default_mutation(graph.vs(1), ('a', 'b', 'c'), 1.0)
        self.assertEqual(res, 'a')

    def test_default_mutation_three(self):
        graph = ig.Graph.Full(3)
        res = default_mutation(graph.vs(1), ('a', 'b', 'c'), 0.0)
        self.assertIn(res, ('b', 'c'))


if __name__ == '__main__':
    unittest.main()
