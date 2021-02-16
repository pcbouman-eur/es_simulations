# -*- coding: utf-8 -*-
import unittest
from decimal import Decimal

from electoral_sys.seat_assignment import jefferson_method, simple_rule


class ElectionResultsOne:

    def __init__(self):
        self.votes = {'a': 100000, 'b': 80000, 'c': 30000, 'd': 20000}
        self.all_votes = sum(self.votes.values())
        self.fractions = {party: Decimal(vote_num) / self.all_votes for party, vote_num in self.votes.items()}
        self.all_seats = 8


class ElectionResultsTwo:

    def __init__(self):
        self.votes = {'a': 100000, 'b': 99000, 'c': 30000, 'd': 30000}
        self.all_votes = sum(self.votes.values())
        self.fractions = {party: Decimal(vote_num) / self.all_votes for party, vote_num in self.votes.items()}
        self.all_seats = 7


class TestSeatAssignment(unittest.TestCase):

    def test_jefferson_one(self):
        election = ElectionResultsOne()
        allocation = jefferson_method(election.all_seats, election.fractions)
        self.assertDictEqual(allocation, {'a': 4, 'b': 3, 'c': 1, 'd': 0})

    def test_jefferson_two(self):
        election = ElectionResultsTwo()
        allocation = jefferson_method(election.all_seats, election.fractions)
        self.assertEqual(allocation['a'], 3)
        self.assertEqual(allocation['b'], 3)
        # last seat will be assigned at random due to the draw
        self.assertEqual(allocation['c'] + allocation['d'], 1)

    def test_simple_rule_one(self):
        election = ElectionResultsOne()
        allocation = simple_rule(election.all_seats, election.fractions)
        self.assertDictEqual(allocation, {'a': 3, 'b': 3, 'c': 1, 'd': 1})

    def test_simple_rule_two(self):
        election = ElectionResultsTwo()
        allocation = jefferson_method(election.all_seats, election.fractions)
        self.assertEqual(allocation['a'], 3)
        self.assertEqual(allocation['b'], 3)
        # last seat will be assigned at random due to the draw
        self.assertEqual(allocation['c'] + allocation['d'], 1)


if __name__ == '__main__':
    unittest.main()
