# -*- coding: utf-8 -*-
import unittest
import igraph as ig
from decimal import Decimal

from electoral_sys.electoral_system import apply_threshold, single_district_voting
from electoral_sys.electoral_system import multi_district_voting, merged_districts_voting
from electoral_sys.seat_assignment import hare_quota, jefferson_method, first_past_the_post


class VotersOne:

    def __init__(self):
        # 5 parties, 4 main districts, full win of one party in each district
        self.all_votes = 230001
        g = ig.Graph(self.all_votes)

        g.vs[0:100001]['district'] = 0  # 100001 voters
        g.vs[100001:180001]['district'] = 1  # 80000 voters
        g.vs[180001:210001]['district'] = 2  # 30000 voters
        g.vs[210001:230001]['district'] = 3  # 20000 voters

        g.vs[0:100001]['state'] = 'a'  # 100001 votes
        g.vs[100001:180001]['state'] = 'b'  # 80000 votes
        g.vs[180001:210001]['state'] = 'c'  # 30000 votes
        g.vs[210001:230001]['state'] = 'd'  # 20000 votes

        self.votes = {'a': 100001, 'b': 80000, 'c': 30000, 'd': 20000, 'e': 0}
        self.vote_fractions = {p: Decimal(v) / self.all_votes for p, v in self.votes.items()}

        self.states = ['a', 'b', 'c', 'd', 'e']  # party 'e' has no votes
        self.voters = g.vs


class VotersTwo:

    def __init__(self):
        # 6 parties, 3 main districts
        self.all_votes = 230000
        g = ig.Graph(self.all_votes)

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
        g.vs[180000:229990]['state'] = 'e'  # 49990 votes
        g.vs[229990:230000]['state'] = 'f'  # 10 votes

        self.votes = {'a': 50002, 'b': 0, 'c': 69999, 'd': 39999, 'e': 69990, 'f': 10}
        self.vote_fractions = {p: Decimal(v) / self.all_votes for p, v in self.votes.items()}

        self.states = ['a', 'b', 'c', 'd', 'e', 'f']  # party 'b' has no votes
        self.voters = g.vs


def eq_seat_assign(total_seats, vote_fractions=None, votes=None, total_votes=None):
    return {party: int(total_seats / len(vote_fractions.keys())) for party in votes.keys()}


class TestElectoralSystems(unittest.TestCase):

    def test_single_dist_voting_one_hare_q(self):
        v = VotersOne()
        t_seats = 8
        res = single_district_voting(v.voters, states=v.states, total_seats=t_seats, assignment_func=hare_quota,
                                     seats_per_district=[], dist_merging=[])
        seats = {'a': 3, 'b': 3, 'c': 1, 'd': 1, 'e': 0}
        self.assertDictEqual(res['seats'], seats)
        self.assertDictEqual(res['seat_fractions'], {p: Decimal(v) / t_seats for p, v in seats.items()})
        self.assertDictEqual(res['votes'], v.votes)
        self.assertDictEqual(res['vote_fractions'], v.vote_fractions)

    def test_single_dist_voting_one_jefferson(self):
        v = VotersOne()
        t_seats = 8
        res = single_district_voting(v.voters, states=v.states, total_seats=t_seats, assignment_func=jefferson_method)
        seats = {'a': 4, 'b': 3, 'c': 1, 'd': 0, 'e': 0}
        self.assertDictEqual(res['seats'], seats)
        self.assertDictEqual(res['seat_fractions'], {p: Decimal(v) / t_seats for p, v in seats.items()})
        self.assertDictEqual(res['votes'], v.votes)
        self.assertDictEqual(res['vote_fractions'], v.vote_fractions)

    def test_single_dist_voting_one_eq_seat_assign(self):
        v = VotersOne()
        t_seats = 500
        res = single_district_voting(v.voters, states=v.states, total_seats=t_seats, assignment_func=eq_seat_assign)
        seats = {'a': 100, 'b': 100, 'c': 100, 'd': 100, 'e': 100}
        self.assertDictEqual(res['seats'], seats)
        self.assertDictEqual(res['seat_fractions'], {p: Decimal(v) / t_seats for p, v in seats.items()})
        self.assertDictEqual(res['votes'], v.votes)
        self.assertDictEqual(res['vote_fractions'], v.vote_fractions)

    def test_single_dist_voting_two_hare_q(self):
        v = VotersTwo()
        t_seats = 23
        res = single_district_voting(v.voters, states=v.states, total_seats=t_seats, assignment_func=hare_quota)
        seats = {'a': 5, 'b': 0, 'c': 7, 'd': 4, 'e': 7, 'f': 0}
        self.assertDictEqual(res['seats'], seats)
        self.assertDictEqual(res['seat_fractions'], {p: Decimal(v) / t_seats for p, v in seats.items()})
        self.assertDictEqual(res['votes'], v.votes)
        self.assertDictEqual(res['vote_fractions'], v.vote_fractions)

    ############################################################################################################

    def test_multi_dist_voting_one_hare_q(self):
        v = VotersOne()
        s_per_dist = [24, 17, 11, 8]
        res = multi_district_voting(v.voters, states=v.states, total_seats=sum(s_per_dist), assignment_func=hare_quota,
                                    seats_per_district=s_per_dist, dist_merging=[])
        seats = {'a': 24, 'b': 17, 'c': 11, 'd': 8, 'e': 0}
        self.assertDictEqual(res['seats'], seats)
        self.assertDictEqual(res['seat_fractions'], {p: Decimal(v) / sum(s_per_dist) for p, v in seats.items()})
        self.assertDictEqual(res['votes'], v.votes)
        self.assertDictEqual(res['vote_fractions'], v.vote_fractions)

    def test_multi_dist_voting_one_eq_seat_assign(self):
        v = VotersOne()
        s_per_dist = [25, 15, 55, 45]
        res = multi_district_voting(v.voters, states=v.states, total_seats=sum(s_per_dist),
                                    assignment_func=eq_seat_assign, seats_per_district=s_per_dist)
        seats = {'a': 28, 'b': 28, 'c': 28, 'd': 28, 'e': 28}
        self.assertDictEqual(res['seats'], seats)
        self.assertDictEqual(res['seat_fractions'], {p: Decimal(v) / sum(s_per_dist) for p, v in seats.items()})
        self.assertDictEqual(res['votes'], v.votes)
        self.assertDictEqual(res['vote_fractions'], v.vote_fractions)

    def test_multi_dist_voting_two_fptp(self):
        v = VotersTwo()
        s_per_dist = [11, 9, 4]
        res = multi_district_voting(v.voters, states=v.states, total_seats=sum(s_per_dist),
                                    assignment_func=first_past_the_post, seats_per_district=s_per_dist)
        seats = {'a': 9, 'b': 0, 'c': 11, 'd': 0, 'e': 4, 'f': 0}
        self.assertDictEqual(res['seats'], seats)
        self.assertDictEqual(res['seat_fractions'], {p: Decimal(v) / sum(s_per_dist) for p, v in seats.items()})
        self.assertDictEqual(res['votes'], v.votes)
        self.assertDictEqual(res['vote_fractions'], v.vote_fractions)

    def test_multi_dist_voting_two_hare_q(self):
        v = VotersTwo()
        s_per_dist = [20, 16, 3]
        res = multi_district_voting(v.voters, states=v.states, total_seats=sum(s_per_dist),
                                    assignment_func=hare_quota, seats_per_district=s_per_dist)
        seats = {'a': 10, 'b': 0, 'c': 14, 'd': 8, 'e': 7, 'f': 0}
        self.assertDictEqual(res['seats'], seats)
        self.assertDictEqual(res['seat_fractions'], {p: Decimal(v) / sum(s_per_dist) for p, v in seats.items()})
        self.assertDictEqual(res['votes'], v.votes)
        self.assertDictEqual(res['vote_fractions'], v.vote_fractions)

    #############################################################################################################

    def test_merged_dist_voting_one_hare_q(self):
        v = VotersOne()
        s_per_dist = [7, 7, 4, 5]
        res = merged_districts_voting(v.voters, states=v.states, total_seats=sum(s_per_dist),
                                      assignment_func=hare_quota, seats_per_district=s_per_dist,
                                      dist_merging=[8, 4, 4, 8])
        seats = {'a': 10, 'b': 8, 'c': 3, 'd': 2, 'e': 0}
        self.assertDictEqual(res['seats'], seats)
        self.assertDictEqual(res['seat_fractions'], {p: Decimal(v) / sum(s_per_dist) for p, v in seats.items()})
        self.assertDictEqual(res['votes'], v.votes)
        self.assertDictEqual(res['vote_fractions'], v.vote_fractions)

    def test_merged_dist_voting_one_fptp(self):
        v = VotersOne()
        s_per_dist = [7, 7, 4, 5]
        res = merged_districts_voting(v.voters, states=v.states, total_seats=sum(s_per_dist),
                                      assignment_func=first_past_the_post, seats_per_district=s_per_dist,
                                      dist_merging=[0, 1, 1, 0])
        seats = {'a': 12, 'b': 11, 'c': 0, 'd': 0, 'e': 0}
        self.assertDictEqual(res['seats'], seats)
        self.assertDictEqual(res['seat_fractions'], {p: Decimal(v) / sum(s_per_dist) for p, v in seats.items()})
        self.assertDictEqual(res['votes'], v.votes)
        self.assertDictEqual(res['vote_fractions'], v.vote_fractions)

    def test_merged_dist_voting_one_fptp_merge_all(self):
        v = VotersOne()
        s_per_dist = [7, 7, 4, 5]
        res = merged_districts_voting(v.voters, states=v.states, total_seats=sum(s_per_dist),
                                      assignment_func=first_past_the_post, seats_per_district=s_per_dist,
                                      dist_merging=[0, 0, 0, 0])
        seats = {'a': 23, 'b': 0, 'c': 0, 'd': 0, 'e': 0}
        self.assertDictEqual(res['seats'], seats)
        self.assertDictEqual(res['seat_fractions'], {p: Decimal(v) / sum(s_per_dist) for p, v in seats.items()})
        self.assertDictEqual(res['votes'], v.votes)
        self.assertDictEqual(res['vote_fractions'], v.vote_fractions)

    def test_merged_dist_voting_two_hare_q(self):
        v = VotersTwo()
        s_per_dist = [20, 16, 10]
        res = merged_districts_voting(v.voters, states=v.states, total_seats=sum(s_per_dist),
                                      assignment_func=hare_quota, seats_per_district=s_per_dist,
                                      dist_merging=[0, 1, 0])
        seats = {'a': 10, 'b': 0, 'c': 14, 'd': 8, 'e': 14, 'f': 0}
        self.assertDictEqual(res['seats'], seats)
        self.assertDictEqual(res['seat_fractions'], {p: Decimal(v) / sum(s_per_dist) for p, v in seats.items()})
        self.assertDictEqual(res['votes'], v.votes)
        self.assertDictEqual(res['vote_fractions'], v.vote_fractions)

    def test_merged_dist_voting_two_hare_q_no_merging(self):
        v = VotersTwo()
        s_per_dist = [20, 16, 3]
        res = merged_districts_voting(v.voters, states=v.states, total_seats=sum(s_per_dist),
                                      assignment_func=hare_quota, seats_per_district=s_per_dist,
                                      dist_merging=[0, 1, 2])
        seats = {'a': 10, 'b': 0, 'c': 14, 'd': 8, 'e': 7, 'f': 0}
        self.assertDictEqual(res['seats'], seats)
        self.assertDictEqual(res['seat_fractions'], {p: Decimal(v) / sum(s_per_dist) for p, v in seats.items()})
        self.assertDictEqual(res['votes'], v.votes)
        self.assertDictEqual(res['vote_fractions'], v.vote_fractions)

    def test_merged_dist_voting_two_hare_q_merge_all(self):
        v = VotersTwo()
        s_per_dist = [1, 4, 18]
        res = merged_districts_voting(v.voters, states=v.states, total_seats=sum(s_per_dist),
                                      assignment_func=hare_quota, seats_per_district=s_per_dist,
                                      dist_merging=[2, 2, 2])
        seats = {'a': 5, 'b': 0, 'c': 7, 'd': 4, 'e': 7, 'f': 0}
        self.assertDictEqual(res['seats'], seats)
        self.assertDictEqual(res['seat_fractions'], {p: Decimal(v) / sum(s_per_dist) for p, v in seats.items()})
        self.assertDictEqual(res['votes'], v.votes)
        self.assertDictEqual(res['vote_fractions'], v.vote_fractions)

    #############################################################################################################

    def test_apply_threshold_func_call(self):
        # with no threshold all arguments should be just passed
        def test_func(a, b, c, d=None, e=None):
            return a, b, c, d, e

        test_func = apply_threshold(test_func)
        res = test_func(1, 200, 'abcd', d=Decimal('12'), e=[1, 2, 3, 4])
        self.assertEqual(res, (1, 200, 'abcd', Decimal('12'), [1, 2, 3, 4]))

    def test_apply_threshold_func_call_th_zero(self):
        # with 0 threshold all arguments should be just passed
        def test_func(a, b, c, d=None, e=None):
            return a, b, c, d, e

        test_func = apply_threshold(test_func)
        res = test_func(1, 200, 'abcd', e=[1, 2, 3, 4], d=Decimal('12'), threshold=0)
        self.assertEqual(res, (1, 200, 'abcd', Decimal('12'), [1, 2, 3, 4]))

    def test_apply_threshold_small(self):
        # only party 'f' will be excluded, but it wouldn't win any seats anyways
        v = VotersTwo()
        s_per_dist = [20, 16, 3]
        res = merged_districts_voting(v.voters, states=v.states, total_seats=sum(s_per_dist),
                                      assignment_func=hare_quota, seats_per_district=s_per_dist,
                                      dist_merging=[0, 1, 2], threshold=0.01)
        seats = {'a': 10, 'b': 0, 'c': 14, 'd': 8, 'e': 7, 'f': 0}
        self.assertDictEqual(res['seats'], seats)
        self.assertDictEqual(res['seat_fractions'], {p: Decimal(v) / sum(s_per_dist) for p, v in seats.items()})
        self.assertDictEqual(res['votes'], v.votes)
        self.assertDictEqual(res['vote_fractions'], v.vote_fractions)

    def test_apply_threshold_big(self):
        # party 'd' will be excluded and won't win the single seat it would win otherwise
        v = VotersOne()
        t_seats = 8
        res = single_district_voting(v.voters, states=v.states, total_seats=t_seats, assignment_func=hare_quota,
                                     seats_per_district=[], dist_merging=[], threshold=0.1)
        seats = {'a': 4, 'b': 3, 'c': 1, 'd': 0, 'e': 0}
        self.assertDictEqual(res['seats'], seats)
        self.assertDictEqual(res['seat_fractions'], {p: Decimal(v) / t_seats for p, v in seats.items()})
        self.assertDictEqual(res['votes'], v.votes)
        self.assertDictEqual(res['vote_fractions'], v.vote_fractions)

    def test_apply_threshold_very_big(self):
        # only parties 'c' and 'e' will be above the threshold
        v = VotersTwo()
        s_per_dist = [20, 16, 3]
        res = multi_district_voting(v.voters, states=v.states, total_seats=sum(s_per_dist),
                                    assignment_func=hare_quota, seats_per_district=s_per_dist, threshold=0.3)
        seats = {'a': 0, 'b': 0, 'c': 28, 'd': 0, 'e': 11, 'f': 0}
        self.assertDictEqual(res['seats'], seats)
        self.assertDictEqual(res['seat_fractions'], {p: Decimal(v) / sum(s_per_dist) for p, v in seats.items()})
        self.assertDictEqual(res['votes'], v.votes)
        self.assertDictEqual(res['vote_fractions'], v.vote_fractions)


if __name__ == '__main__':
    unittest.main()
