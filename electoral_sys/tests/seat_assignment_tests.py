# -*- coding: utf-8 -*-
import unittest
from decimal import Decimal

from electoral_sys.seat_assignment import jefferson_method, hamilton_method, first_past_the_post
from electoral_sys.seat_assignment import hare_quota, droop_quota, exact_droop_quota, imperiali_quota


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


class ElectionResultsThree:

    def __init__(self):
        self.votes = {'a': 41000, 'b': 29000, 'c': 17000, 'd': 13000, 'e': 15}
        self.all_votes = sum(self.votes.values())
        self.fractions = {party: Decimal(vote_num) / self.all_votes for party, vote_num in self.votes.items()}
        self.all_seats = 8


class ElectionOneSeat:  # todo check it for all methods passing all arguments

    def __init__(self):
        self.votes = {'a': 213512, 'b': 113512, 'c': 393545, 'd': 0, 'e': 124}
        self.all_votes = sum(self.votes.values())
        self.fractions = {party: Decimal(vote_num) / self.all_votes for party, vote_num in self.votes.items()}
        self.all_seats = 1


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

    def test_jefferson_three(self):
        election = ElectionResultsThree()
        allocation = jefferson_method(election.all_seats, election.fractions)
        self.assertDictEqual(allocation, {'a': 4, 'b': 2, 'c': 1, 'd': 1, 'e': 0})

    def test_hamilton_method_one(self):
        election = ElectionResultsOne()
        allocation = hamilton_method(election.all_seats, vote_fractions=election.fractions)
        self.assertDictEqual(allocation, {'a': 3, 'b': 3, 'c': 1, 'd': 1})

    def test_hamilton_method_two(self):
        election = ElectionResultsTwo()
        allocation = hamilton_method(election.all_seats, vote_fractions=election.fractions)
        self.assertEqual(allocation['a'], 3)
        self.assertEqual(allocation['b'], 2)
        self.assertEqual(allocation['c'], 1)
        self.assertEqual(allocation['d'], 1)

    def test_fptp_rule_one(self):
        election = ElectionResultsOne()
        allocation = first_past_the_post(election.all_seats, vote_fractions=election.fractions)
        self.assertDictEqual(allocation, {'a': election.all_seats, 'b': 0, 'c': 0, 'd': 0})

    def test_fptp_rule_one_seat(self):
        allocation = first_past_the_post(1, vote_fractions={'a': Decimal('0.13'), 'b': Decimal('0.26'),
                                                            'c': Decimal('0.31'), 'd': Decimal('0.09'),
                                                            'f': Decimal('0.29')})
        self.assertDictEqual(allocation, {'a': 0, 'b': 0, 'c': 1, 'd': 0, 'f': 0})

    def test_fptp_rule_random(self):
        # the winner is random because of the draw
        allocation = first_past_the_post(1, vote_fractions={'a': Decimal('0.4'), 'b': Decimal('0.4'),
                                                            'c': Decimal('0.2')})
        self.assertEqual(allocation['a'] + allocation['b'], 1)

    def test_hare_quota_one(self):
        election = ElectionResultsOne()
        allocation = hare_quota(election.all_seats, votes=election.votes, total_votes=election.all_votes)
        self.assertDictEqual(allocation, {'a': 3, 'b': 3, 'c': 1, 'd': 1})

    def test_hare_quota_two(self):
        election = ElectionResultsTwo()
        allocation = hare_quota(election.all_seats, votes=election.votes, total_votes=election.all_votes)
        self.assertDictEqual(allocation, {'a': 3, 'b': 2, 'c': 1, 'd': 1})

    def test_hare_quota_three(self):
        election = ElectionResultsThree()
        allocation = hare_quota(election.all_seats, votes=election.votes, total_votes=election.all_votes)
        self.assertDictEqual(allocation, {'a': 3, 'b': 2, 'c': 2, 'd': 1, 'e': 0})

    def test_hare_quota_random(self):
        allocation = hare_quota(9, votes={'a': 12345, 'b': 12345, 'c': 0}, total_votes=12345+12345)
        # last seat will be assigned at random due to the draw
        self.assertGreaterEqual(allocation['a'], 4)
        self.assertGreaterEqual(allocation['b'], 4)
        # last seat will be assigned at random due to the draw
        self.assertEqual(allocation['a'] + allocation['b'], 9)
        self.assertEqual(allocation['c'], 0)

    def test_droop_quota_one(self):
        election = ElectionResultsOne()
        allocation = droop_quota(election.all_seats, votes=election.votes, total_votes=election.all_votes)
        self.assertDictEqual(allocation, {'a': 4, 'b': 3, 'c': 1, 'd': 0})

    def test_droop_quota_two(self):
        election = ElectionResultsTwo()
        allocation = droop_quota(election.all_seats, votes=election.votes, total_votes=election.all_votes)
        self.assertEqual(allocation['a'], 3)
        self.assertEqual(allocation['b'], 3)
        # last seat will be assigned at random due to the draw
        self.assertEqual(allocation['c'] + allocation['d'], 1)

    def test_droop_quota_three(self):
        election = ElectionResultsThree()
        allocation = droop_quota(election.all_seats, votes=election.votes, total_votes=election.all_votes)
        self.assertDictEqual(allocation, {'a': 4, 'b': 2, 'c': 1, 'd': 1, 'e': 0})

    def test_droop_quota_random(self):
        allocation = droop_quota(3, votes={'a': 60000, 'b': 20000, 'c': 20000}, total_votes=100000)
        self.assertEqual(allocation['a'], 2)
        # last seat will be assigned at random due to the draw
        self.assertEqual(allocation['b'] + allocation['c'], 1)

    def test_exact_droop_quota_one(self):
        election = ElectionResultsOne()
        allocation = exact_droop_quota(election.all_seats, votes=election.votes, total_votes=election.all_votes)
        self.assertDictEqual(allocation, {'a': 4, 'b': 3, 'c': 1, 'd': 0})

    def test_exact_droop_quota_two(self):
        election = ElectionResultsTwo()
        allocation = exact_droop_quota(election.all_seats, votes=election.votes, total_votes=election.all_votes)
        self.assertEqual(allocation['a'], 3)
        self.assertEqual(allocation['b'], 3)
        # last seat will be assigned at random due to the draw
        self.assertEqual(allocation['c'] + allocation['d'], 1)

    def test_exact_droop_quota_three(self):
        election = ElectionResultsThree()
        allocation = exact_droop_quota(election.all_seats, votes=election.votes, total_votes=election.all_votes)
        self.assertDictEqual(allocation, {'a': 4, 'b': 2, 'c': 1, 'd': 1, 'e': 0})

    def test_exact_droop_quota_random(self):
        allocation = exact_droop_quota(3, votes={'a': 60000, 'b': 20000, 'c': 20000}, total_votes=100000)
        self.assertEqual(allocation['a'], 2)
        # last seat will be assigned at random due to the draw
        self.assertEqual(allocation['b'] + allocation['c'], 1)

    def test_exact_droop_quota_too_many_seats(self):
        allocation = exact_droop_quota(3, votes={'a': 634626, 'b': 0, 'c': 0}, total_votes=634626)
        self.assertDictEqual(allocation, {'a': 3, 'b': 0, 'c': 0})

    def test_imperiali_quota_one(self):
        election = ElectionResultsOne()
        allocation = imperiali_quota(election.all_seats, votes=election.votes, total_votes=election.all_votes)
        self.assertDictEqual(allocation, {'a': 4, 'b': 3, 'c': 1, 'd': 0})

    def test_imperiali_quota_two(self):
        # too many seats will be assigned, so the exact droop quota will be used
        election = ElectionResultsTwo()
        allocation = imperiali_quota(election.all_seats, votes=election.votes, total_votes=election.all_votes)
        self.assertEqual(allocation['a'], 3)
        self.assertEqual(allocation['b'], 3)
        # last seat will be assigned at random due to the draw
        self.assertEqual(allocation['c'] + allocation['d'], 1)

    def test_imperiali_quota_three(self):
        election = ElectionResultsThree()
        allocation = imperiali_quota(election.all_seats, votes=election.votes, total_votes=election.all_votes)
        self.assertDictEqual(allocation, {'a': 4, 'b': 2, 'c': 1, 'd': 1, 'e': 0})

    def test_imperiali_quota_random(self):
        allocation = imperiali_quota(4, votes={'a': 333333, 'b': 333333, 'c': 333333}, total_votes=333333*3)
        self.assertGreaterEqual(allocation['a'], 1)
        self.assertGreaterEqual(allocation['b'], 1)
        self.assertGreaterEqual(allocation['c'], 1)
        # last seat will be assigned at random due to the draw
        self.assertEqual(sum(allocation.values()), 4)

    def test_imperiali_quota_too_many_seats(self):
        # too many seats will be assigned, the exact droop quota will be used, which will then also increase the quota
        allocation = imperiali_quota(3, votes={'a': 96436994576, 'b': 0, 'c': 0}, total_votes=96436994576)
        self.assertDictEqual(allocation, {'a': 3, 'b': 0, 'c': 0})


if __name__ == '__main__':
    unittest.main()
