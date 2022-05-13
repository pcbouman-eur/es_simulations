# -*- coding: utf-8 -*-
import unittest
import igraph as ig
from decimal import Decimal
from collections import Counter
from unittest.mock import patch

from simulation.base import default_mutation, default_propagation, majority_propagation
from simulation.base import run_simulation, run_thermalization, run_thermalization_simple


class TestGraphNine(ig.Graph):
    """
    this test graph is design to have 9 nodes, so initialize it like 'TestGraphNine(9)'
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vs['state'] = 'b'
        self.vs[2]['state'] = 'a'
        self.vs[6]['state'] = 'c'
        self.vs[7]['state'] = 'c'
        self.vs[8]['state'] = 'c'
        self.vs[0]['state'] = 'c'
        self.vs['zealot'] = 0
        self.add_edge(1, 2)
        self.add_edge(2, 3)
        self.add_edge(2, 4)
        self.add_edge(2, 5)
        self.add_edge(4, 7)
        self.add_edge(5, 6)
        self.add_edge(5, 8)
        self.add_edge(6, 8)


class Configuration:
    """
    dummy configuration with propagate and mutate methods and thermalization
    """
    all_states = None
    mass_media = None
    total_seats = None
    seat_alloc_function = None

    @staticmethod
    def propagate(node, g):
        return 'abcdef'

    @staticmethod
    def mutate(node, all_states, p):
        # to check if all_states and mass_media are being passed correctly in run_simulation
        return all_states + 'ghijk' + p


def eq_seat_assign(total_seats, vote_fractions=None, votes=None, total_votes=None):
    return {party: int(total_seats / len(vote_fractions.keys())) for party in votes.keys()}


class TestSimulationBase(unittest.TestCase):

    def test_default_mutation_one(self):
        graph = ig.Graph.Full(3)
        res = default_mutation(graph.vs[1], ('a', 'b', 'c'), 1.0/3)
        self.assertIn(res, ('a', 'b', 'c'))

    def test_default_mutation_two(self):
        graph = ig.Graph.Full(3)
        res = default_mutation(graph.vs[1], ('a', 'b', 'c'), 1.0)
        self.assertEqual(res, 'a')

    def test_default_mutation_three(self):
        graph = ig.Graph.Full(3)
        res = default_mutation(graph.vs[1], ('a', 'b', 'c'), 0.0)
        self.assertIn(res, ('b', 'c'))

    def test_default_propagation(self):
        g = TestGraphNine(9)
        state = default_propagation(g.vs[2], g)  # all neighbours are 'b'
        self.assertEqual(state, 'b')
        state = default_propagation(g.vs[3], g)  # the only neighbour is 'a'
        self.assertEqual(state, 'a')

    def test_default_propagation_no_neighbours(self):
        g = ig.Graph(3)
        g.vs['state'] = ['a', 'b', 'c']
        state = default_propagation(g.vs[1], g)
        self.assertEqual(state, 'b')

    def test_majority_propagation(self):
        g = TestGraphNine(9)
        state = majority_propagation(g.vs[2], g)  # all neighbours are 'b'
        self.assertEqual(state, 'b')
        state = majority_propagation(g.vs[3], g)  # the only neighbour is 'a'
        self.assertEqual(state, 'a')
        state = majority_propagation(g.vs[5], g)  # two neighbours are 'c' and one is 'a'
        self.assertEqual(state, 'c')
        state = majority_propagation(g.vs[8], g)  # one neighbour is 'c' and one is 'b'
        self.assertIn(state, ['b', 'c'])

    def test_majority_propagation_inverse(self):
        g = TestGraphNine(9)
        state = majority_propagation(g.vs[2], g, inverse=True)  # all neighbours are 'b'
        self.assertEqual(state, 'b')
        state = majority_propagation(g.vs[3], g, inverse=True)  # the only neighbour is 'a'
        self.assertEqual(state, 'a')
        state = majority_propagation(g.vs[5], g, inverse=True)  # two neighbours are 'c' and one is 'a'
        self.assertEqual(state, 'a')
        state = majority_propagation(g.vs[8], g, inverse=True)  # one neighbour is 'c' and one is 'b'
        self.assertIn(state, ['b', 'c'])

    def test_majority_propagation_no_neighbours(self):
        g = ig.Graph(3)
        g.vs['state'] = ['a', 'b', 'c']
        state = majority_propagation(g.vs[1], g)
        self.assertEqual(state, 'b')

    def test_run_simulation_propagate(self):
        noise_rate = 0
        g = TestGraphNine(9)
        config = Configuration()
        g = run_simulation(config, g, noise_rate, 1, n=9)
        self.assertIn('abcdef', g.vs['state'])
        self.assertEqual(Counter(g.vs['state'])['abcdef'], 1)

    def test_run_simulation_propagate_no_n(self):
        noise_rate = 0
        g = TestGraphNine(9)
        config = Configuration()
        g = run_simulation(config, g, noise_rate, 1)
        self.assertIn('abcdef', g.vs['state'])
        self.assertEqual(Counter(g.vs['state'])['abcdef'], 1)

    def test_run_simulation_mutate(self):
        noise_rate = 1
        g = TestGraphNine(9)
        config = Configuration()
        config.all_states = 'qqq'
        config.mass_media = 'ccc'
        g = run_simulation(config, g, noise_rate, 1, n=9)
        self.assertIn('qqqghijkccc', g.vs['state'])
        self.assertEqual(Counter(g.vs['state'])['qqqghijkccc'], 1)

    def test_run_simulation_steps_count(self):
        global steps_count
        steps_count = 0

        def one_step(*args, **kwargs):
            global steps_count
            steps_count += 1
            return 'a'

        noise_rate = 0.5
        g = TestGraphNine(9)
        config = Configuration()
        config.mutate = one_step
        config.propagate = one_step

        g = run_simulation(config, g, noise_rate, 124, n=9)
        self.assertEqual(steps_count, 124)

    def test_run_simulation_zealots(self):
        noise_rate = 0.5
        g = TestGraphNine(9)
        g.vs['zealot'] = 1
        config = Configuration()
        g = run_simulation(config, g, noise_rate, 100, n=9)
        self.assertListEqual(g.vs['state'], ['c', 'b', 'a', 'b', 'b', 'b', 'c', 'c', 'c'])

    @patch('simulation.base.run_simulation')
    def test_run_thermalization_simple(self, mocked_run):
        noise_rate = 0.2
        g = TestGraphNine(9)
        config = Configuration()
        run_thermalization_simple(config, g, noise_rate, 1, n=9)
        mocked_run.assert_called_once_with(config, g, noise_rate, 1, n=9)

    @patch('simulation.base.run_simulation')
    def test_run_thermalization(self, mocked_run):
        # this test relies on electoral_sys.electoral_system.single_district_voting(),
        # because it can not be mocked without doing black magic, because it's decorated
        noise_rate = 0.2
        g = TestGraphNine(9)
        g.add_vertex()
        g.vs[0:5]['state'] = 'a'
        g.vs[5:10]['state'] = 'b'

        mocked_run.return_value = g

        config = Configuration()
        config.all_states = ['a', 'b']
        config.total_seats = 15
        config.seat_alloc_function = eq_seat_assign

        res_g, trajectory = run_thermalization(config, g, noise_rate, 5000, n=9)
        mocked_run.assert_called_with(config, g, noise_rate, 1000, n=9)
        self.assertEqual(mocked_run.call_count, 5)
        self.assertEqual(res_g, g)
        self.assertDictEqual(trajectory, {'a': [Decimal('0.5')] * 6,
                                          'b': [Decimal('0.5')] * 6})


if __name__ == '__main__':
    unittest.main()
