# -*- coding: utf-8 -*-
import unittest
import numpy as np
import igraph as ig
from decimal import Decimal

from electoral_sys.electoral_system import apply_threshold, single_district_voting
from electoral_sys.electoral_system import multi_district_voting, merged_districts_voting
from electoral_sys.seat_assignment import hare_quota, jefferson_method, first_past_the_post


class VotersOne:

    def __init__(self):
        # 5 parties, 4 main districts, full win of one party in each district
        g = ig.Graph(230001)

        g.vs[0:100001]['district'] = 0  # 100001 voters
        g.vs[100001:180001]['district'] = 1  # 80000 voters
        g.vs[180001:210001]['district'] = 2  # 30000 voters
        g.vs[210001:230001]['district'] = 3  # 20000 voters

        g.vs[0:100001]['state'] = 'a'  # 100001 votes
        g.vs[100001:180001]['state'] = 'b'  # 80000 votes
        g.vs[180001:210001]['state'] = 'c'  # 30000 votes
        g.vs[210001:230001]['state'] = 'd'  # 20000 votes

        self.states = ['a', 'b', 'c', 'd', 'e']  # party 'e' has no votes
        self.voters = g.vs


class VotersTwo:

    def __init__(self):
        # 6 parties, 3 main districts
        g = ig.Graph(230000)

        # 1st DISTRICT
        g.vs[0:100000]['district'] = 0  # 100000 voters
        g.vs[0:30000]['state'] = 'a'  # 30000 votes
        g.vs[30000:80000]['state'] = 'c'  # 50000 voters
        g.vs[80000:100000]['state'] = 'd'  # 20000 voters

        # 2nd DISTRICT
        g.vs[100000:180000]['district'] = 1  # 80000 voters
        g.vs[100000:120002]['state'] = 'a'  # 20002 votes
        g.vs[120002:140001]['state'] = 'c'  # 19999 votes
        g.vs[140001:160000]['state'] = 'd'  # 19999 votes
        g.vs[160000:180000]['state'] = 'e'  # 20000 votes

        # 3rd DISTRICT
        g.vs[180000:230000]['district'] = 2  # 50000 voters
        g.vs[180000:230000]['state'] = 'e'  # 50000 votes

        self.votes = {}
        self.vote_fractions = {}  # TODO

        self.states = ['a', 'b', 'c', 'd', 'e', 'f']  # parties 'b' and 'f' have no votes
        self.voters = g.vs


def eq_seat_assign(total_seats, vote_fractions=None, votes=None, total_votes=None):
    return {party: int(total_seats / len(vote_fractions.keys())) for party in votes.keys()}


class TestElectoralSystems(unittest.TestCase):

    def test_single_dist_voting_one_hare_q(self):
        v = VotersOne()
        res = single_district_voting(v.voters, states=v.states, total_seats=8, assignment_func=hare_quota,
                                     seats_per_district=[], dist_merging=[])
        self.assertDictEqual(res['seats'], {'a': 3, 'b': 3, 'c': 1, 'd': 1, 'e': 0})
        self.assertDictEqual(res['seat_fractions'], {'a': Decimal('0.375'),
                                                     'b': Decimal('0.375'),
                                                     'c': Decimal('0.125'),
                                                     'd': Decimal('0.125'),
                                                     'e': Decimal('0')})
        self.assertDictEqual(res['votes'], {'a': 100001, 'b': 80000, 'c': 30000, 'd': 20000, 'e': 0})
        self.assertDictEqual(res['vote_fractions'], {'a': Decimal('0.4347850661518862961465384933'),
                                                     'b': Decimal('0.3478245746757622792944378503'),
                                                     'c': Decimal('0.1304342155034108547354141939'),
                                                     'd': Decimal('0.08695614366894056982360946257'),
                                                     'e': Decimal('0')})

    def test_single_dist_voting_one_jefferson(self):
        v = VotersOne()
        res = single_district_voting(v.voters, states=v.states, total_seats=8, assignment_func=jefferson_method)
        self.assertDictEqual(res['seats'], {'a': 4, 'b': 3, 'c': 1, 'd': 0, 'e': 0})
        self.assertDictEqual(res['seat_fractions'], {'a': Decimal('0.5'),
                                                     'b': Decimal('0.375'),
                                                     'c': Decimal('0.125'),
                                                     'd': Decimal('0'),
                                                     'e': Decimal('0')})
        self.assertDictEqual(res['votes'], {'a': 100001, 'b': 80000, 'c': 30000, 'd': 20000, 'e': 0})
        self.assertDictEqual(res['vote_fractions'], {'a': Decimal('0.4347850661518862961465384933'),
                                                     'b': Decimal('0.3478245746757622792944378503'),
                                                     'c': Decimal('0.1304342155034108547354141939'),
                                                     'd': Decimal('0.08695614366894056982360946257'),
                                                     'e': Decimal('0')})

    def test_single_dist_voting_one_eq_seat_assign(self):
        v = VotersOne()
        res = single_district_voting(v.voters, states=v.states, total_seats=500, assignment_func=eq_seat_assign)
        self.assertDictEqual(res['seats'], {'a': 100, 'b': 100, 'c': 100, 'd': 100, 'e': 100})
        self.assertDictEqual(res['seat_fractions'], {'a': Decimal('0.2'),
                                                     'b': Decimal('0.2'),
                                                     'c': Decimal('0.2'),
                                                     'd': Decimal('0.2'),
                                                     'e': Decimal('0.2')})
        self.assertDictEqual(res['votes'], {'a': 100001, 'b': 80000, 'c': 30000, 'd': 20000, 'e': 0})
        self.assertDictEqual(res['vote_fractions'], {'a': Decimal('0.4347850661518862961465384933'),
                                                     'b': Decimal('0.3478245746757622792944378503'),
                                                     'c': Decimal('0.1304342155034108547354141939'),
                                                     'd': Decimal('0.08695614366894056982360946257'),
                                                     'e': Decimal('0')})

    def test_single_dist_voting_two_hare_q(self):
        v = VotersTwo()
        res = single_district_voting(v.voters, states=v.states, total_seats=23, assignment_func=hare_quota)
        self.assertDictEqual(res['seats'], {'a': 5, 'b': 0, 'c': 7, 'd': 4, 'e': 7, 'f': 0})
        self.assertDictEqual(res['seat_fractions'], {'a': Decimal('0.2173913043478260869565217391'),
                                                     'b': Decimal('0'),
                                                     'c': Decimal('0.3043478260869565217391304348'),
                                                     'd': Decimal('0.1739130434782608695652173913'),
                                                     'e': Decimal('0.3043478260869565217391304348'),
                                                     'f': Decimal('0')})
        self.assertDictEqual(res['votes'], {'a': 50000, 'b': 0, 'c': 70000, 'd': 40000, 'e': 70000, 'f': 0})
        self.assertDictEqual(res['vote_fractions'], {'a': Decimal('0.2173913043478260869565217391'),
                                                     'b': Decimal('0'),
                                                     'c': Decimal('0.3043478260869565217391304348'),
                                                     'd': Decimal('0.1739130434782608695652173913'),
                                                     'e': Decimal('0.3043478260869565217391304348'),
                                                     'f': Decimal('0')})

    ############################################################################################################

    def test_multi_dist_voting_one_hare_q(self):
        v = VotersOne()
        s_per_dist = [24, 17, 11, 8]
        res = multi_district_voting(v.voters, states=v.states, total_seats=sum(s_per_dist), assignment_func=hare_quota,
                                    seats_per_district=s_per_dist, dist_merging=[])
        self.assertDictEqual(res['seats'], {'a': 24, 'b': 17, 'c': 11, 'd': 8, 'e': 0})
        self.assertDictEqual(res['seat_fractions'], {'a': Decimal('0.4'),
                                                     'b': Decimal('0.2833333333333333333333333333'),
                                                     'c': Decimal('0.1833333333333333333333333333'),
                                                     'd': Decimal('0.1333333333333333333333333333'),
                                                     'e': Decimal('0')})
        self.assertDictEqual(res['votes'], {'a': 100001, 'b': 80000, 'c': 30000, 'd': 20000, 'e': 0})
        self.assertDictEqual(res['vote_fractions'], {'a': Decimal('0.4347850661518862961465384933'),
                                                     'b': Decimal('0.3478245746757622792944378503'),
                                                     'c': Decimal('0.1304342155034108547354141939'),
                                                     'd': Decimal('0.08695614366894056982360946257'),
                                                     'e': Decimal('0')})

    def test_multi_dist_voting_one_eq_seat_assign(self):
        v = VotersOne()
        s_per_dist = [25, 15, 55, 45]
        res = multi_district_voting(v.voters, states=v.states, total_seats=sum(s_per_dist),
                                    assignment_func=eq_seat_assign, seats_per_district=s_per_dist)
        self.assertDictEqual(res['seats'], {'a': 28, 'b': 28, 'c': 28, 'd': 28, 'e': 28})
        self.assertDictEqual(res['seat_fractions'], {'a': Decimal('0.2'),
                                                     'b': Decimal('0.2'),
                                                     'c': Decimal('0.2'),
                                                     'd': Decimal('0.2'),
                                                     'e': Decimal('0.2')})
        self.assertDictEqual(res['votes'], {'a': 100001, 'b': 80000, 'c': 30000, 'd': 20000, 'e': 0})
        self.assertDictEqual(res['vote_fractions'], {'a': Decimal('0.4347850661518862961465384933'),
                                                     'b': Decimal('0.3478245746757622792944378503'),
                                                     'c': Decimal('0.1304342155034108547354141939'),
                                                     'd': Decimal('0.08695614366894056982360946257'),
                                                     'e': Decimal('0')})

    def test_multi_dist_voting_two_fptp(self):
        v = VotersTwo()
        s_per_dist = [11, 9, 4]
        res = multi_district_voting(v.voters, states=v.states, total_seats=sum(s_per_dist),
                                    assignment_func=first_past_the_post, seats_per_district=s_per_dist)
        self.assertDictEqual(res['seats'], {'a': 9, 'b': 0, 'c': 11, 'd': 0, 'e': 4, 'f': 0})
        self.assertDictEqual(res['seat_fractions'], {'a': Decimal('0.375'),
                                                     'b': Decimal('0'),
                                                     'c': Decimal('0.4583333333333333333333333333'),
                                                     'd': Decimal('0'),
                                                     'e': Decimal('0.1666666666666666666666666667'),
                                                     'f': Decimal('0')})
        votes = {'a': 50002, 'b': 0, 'c': 69999, 'd': 39999, 'e': 70000, 'f': 0}  # TODO add this to the VotersTwo class
        self.assertDictEqual(res['votes'], votes)
        self.assertDictEqual(res['vote_fractions'], {p: Decimal(v) / sum(votes.values()) for p, v in votes.items()}) # TODO check the fractions like this in every function
    # TODO add tests for VotersTwo with hare_q, add tests of the threshold

    #############################################################################################################

    def test_merged_dist_voting_one_hare_q(self):
        v = VotersOne()
        s_per_dist = [7, 7, 4, 5]
        res = merged_districts_voting(v.voters, states=v.states, total_seats=sum(s_per_dist),
                                      assignment_func=hare_quota, seats_per_district=s_per_dist,
                                      dist_merging=[8, 4, 4, 8])
        self.assertDictEqual(res['seats'], {'a': 10, 'b': 8, 'c': 3, 'd': 2, 'e': 0})
        self.assertDictEqual(res['seat_fractions'], {'a': Decimal('0.4347826086956521739130434783'),
                                                     'b': Decimal('0.3478260869565217391304347826'),
                                                     'c': Decimal('0.1304347826086956521739130435'),
                                                     'd': Decimal('0.08695652173913043478260869565'),
                                                     'e': Decimal('0')})
        self.assertDictEqual(res['votes'], {'a': 100001, 'b': 80000, 'c': 30000, 'd': 20000, 'e': 0})
        self.assertDictEqual(res['vote_fractions'], {'a': Decimal('0.4347850661518862961465384933'),
                                                     'b': Decimal('0.3478245746757622792944378503'),
                                                     'c': Decimal('0.1304342155034108547354141939'),
                                                     'd': Decimal('0.08695614366894056982360946257'),
                                                     'e': Decimal('0')})

    def test_merged_dist_voting_one_fptp(self):
        v = VotersOne()
        s_per_dist = [7, 7, 4, 5]
        res = merged_districts_voting(v.voters, states=v.states, total_seats=sum(s_per_dist),
                                      assignment_func=first_past_the_post, seats_per_district=s_per_dist,
                                      dist_merging=[0, 1, 1, 0])
        self.assertDictEqual(res['seats'], {'a': 12, 'b': 11, 'c': 0, 'd': 0, 'e': 0})
        self.assertDictEqual(res['seat_fractions'], {'a': Decimal('0.5217391304347826086956521739'),
                                                     'b': Decimal('0.4782608695652173913043478261'),
                                                     'c': Decimal('0'),
                                                     'd': Decimal('0'),
                                                     'e': Decimal('0')})
        self.assertDictEqual(res['votes'], {'a': 100001, 'b': 80000, 'c': 30000, 'd': 20000, 'e': 0})
        self.assertDictEqual(res['vote_fractions'], {'a': Decimal('0.4347850661518862961465384933'),
                                                     'b': Decimal('0.3478245746757622792944378503'),
                                                     'c': Decimal('0.1304342155034108547354141939'),
                                                     'd': Decimal('0.08695614366894056982360946257'),
                                                     'e': Decimal('0')})

    def test_merged_dist_voting_one_fptp_merge_all(self):
        v = VotersOne()
        s_per_dist = [7, 7, 4, 5]
        res = merged_districts_voting(v.voters, states=v.states, total_seats=sum(s_per_dist),
                                      assignment_func=first_past_the_post, seats_per_district=s_per_dist,
                                      dist_merging=[0, 0, 0, 0])
        self.assertDictEqual(res['seats'], {'a': 23, 'b': 0, 'c': 0, 'd': 0, 'e': 0})
        self.assertDictEqual(res['seat_fractions'], {'a': Decimal('1'),
                                                     'b': Decimal('0'),
                                                     'c': Decimal('0'),
                                                     'd': Decimal('0'),
                                                     'e': Decimal('0')})
        self.assertDictEqual(res['votes'], {'a': 100001, 'b': 80000, 'c': 30000, 'd': 20000, 'e': 0})
        self.assertDictEqual(res['vote_fractions'], {'a': Decimal('0.4347850661518862961465384933'),
                                                     'b': Decimal('0.3478245746757622792944378503'),
                                                     'c': Decimal('0.1304342155034108547354141939'),
                                                     'd': Decimal('0.08695614366894056982360946257'),
                                                     'e': Decimal('0')})


if __name__ == '__main__':
    unittest.main()
