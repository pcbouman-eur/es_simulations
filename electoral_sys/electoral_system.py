# -*- coding: utf-8 -*-
"""
Functions used to model different election systems and apply them to the distributions of voters
"""
from decimal import Decimal
from collections import Counter

from configuration.logging import log
from electoral_sys.seat_assignment import simple_rule as default_assignment


###########################################################
#                                                         #
#                Electoral threshold                      #
#                                                         #
###########################################################

def apply_threshold(system_func):
    """
    Decorator for threshold application. Every function representing electoral system should be decorated.
    :param system_func: a function representing electoral system
    :return: decorated function
    """
    def inner(voters, *args, threshold=0.0, **kwargs):
        """
        Function applying the electoral threshold (minimal share of total votes to be considered at all)
        and returning only voters of those parties that are above the threshold.
        :param voters: collection of voters with 'state' and 'district' parameters, igraph.VertexSeq object
        :param threshold: the electoral entry threshold (float)
        :return: the original electoral system function
        """
        if threshold != 0.0:
            res_no_threshold = single_district_voting(voters, *args, **kwargs)

            # get the parties below threshold, which should be fewer than above
            excluded_parties = [party for party, vote_share in res_no_threshold['vote_fractions'].items()
                                if vote_share < Decimal(str(threshold))]

            # indexes of vertices which are above threshold
            if excluded_parties:
                new_voters = voters.select(state_notin=excluded_parties)

                # check if any party has made it above the threshold to avoid issues
                if len(new_voters) > 0:
                    voters = new_voters
                else:
                    # this shouldn't happen in reasonable scenarios
                    log.error('No party has reached the entry threshold, so the threshold is being ignored')

            res = system_func(voters, *args, **kwargs)

            # we want the absolute fraction of votes casted for each party to compute proportionality indexes etc.
            return dict(res, vote_fractions=res_no_threshold['vote_fractions'], votes=res_no_threshold['votes'])
        else:
            return system_func(voters, *args, **kwargs)

    return inner


###########################################################
#                                                         #
#               Vote-counting functions                   #
#                                                         #
###########################################################


@apply_threshold
def single_district_voting(voters, states=None, total_seats=None, assignment_func=None, **kw):
    """
    Counts the votes casted for each party and then computes the fraction of votes obtained
    and the number and fraction of seats obtained in the considered district.
    :param voters: igraph.VertexSeq object, collection of voters  in the considered district with a 'state' parameter
    :param states: all possible states of voters (votes), should be provided in order to get the losers in the results
    :param total_seats: the total number of seats available in the district
    :param assignment_func: the function to use for assigning seats for parties
    :return: the number and the fraction of votes obtained, and the number and the fraction of seats obtained, per party
    """
    # count the votes for every state/party, making sure that parties with 0 votes are also in the counter
    votes = Counter(voters['state'])
    if states is not None:
        for party in states:
            if party not in votes:
                votes[party] = 0

    total_votes = sum(votes.values())
    vote_fractions = {party: Decimal(v) / Decimal(total_votes) for party, v in votes.items()}

    # compute the seats obtained within the considered district
    seat_assignment = Counter(assignment_func(total_seats, vote_fractions=vote_fractions,
                                              votes=votes, total_votes=total_votes))
    seat_fractions = {party: Decimal(seats) / Decimal(total_seats) for party, seats in seat_assignment.items()}

    return {'seat_fractions': seat_fractions, 'seats': seat_assignment, 'vote_fractions': vote_fractions,
            'votes': votes}


@apply_threshold
def multi_district_voting(voters, states=None, total_seats=None, assignment_func=None, seats_per_district=None, **kw):
    """
    Counts the votes casted for each party and the number of seats obtained in each district separately.
    Then computes the fraction of votes obtained and the fraction of seats won globally,
    and returns aggregated results.
    :param voters: igraph.VertexSeq object, collection of voters  in the considered district with a 'state' parameter
    :param states: all possible states of voters (votes), should be provided in order to get the losers in the results
    :param total_seats: the total number of seats available in the district
    :param assignment_func: the function to use for assigning seats for parties
    :param seats_per_district: a list with the number of seats per district,
    index of the list entry corresponds to the number of the district
    :return: the number and the fraction of votes obtained, and the number and the fraction of seats obtained, per party
    """
    seat_assignment = Counter()
    votes = Counter()

    # get the results for every district separately
    for district in range(len(seats_per_district)):
        district_res = single_district_voting(voters.select(district_eq=district), states=states,
                                              total_seats=seats_per_district[district], assignment_func=assignment_func)
        seat_assignment += district_res['seats']
        votes += district_res['votes']

    # summation of counters above deletes the counts with value 0 from the result
    if states is not None:
        for party in states:
            if party not in seat_assignment:
                seat_assignment[party] = 0
            if party not in votes:
                votes[party] = 0

    vote_fractions = {party: Decimal(v) / Decimal(sum(votes.values())) for party, v in votes.items()}
    seat_fractions = {party: Decimal(s) / Decimal(total_seats) for party, s in seat_assignment.items()}

    # the final result is the aggregated result based on seats won in all districts
    return {'seat_fractions': seat_fractions, 'seats': seat_assignment, 'vote_fractions': vote_fractions,
            'votes': votes}


@apply_threshold
def merged_districts_voting(voters, states=None, total_seats=None, assignment_func=None, seats_per_district=None,
                            dist_merging=None, **kw):
    """
    Works like multi_district_voting(), but the electoral districts are made of groups of main districts,
    where the main districts are indicated by the 'district' attribute of the voters, as always.
    Merging is performed based on the dist_merging parameter.
    :param voters: igraph.VertexSeq object, collection of voters  in the considered district with a 'state' parameter
    :param states: all possible states of voters (votes), should be provided in order to get the losers in the results
    :param total_seats: the total number of seats available in the district
    :param assignment_func: the function to use for assigning seats for parties
    :param seats_per_district: a list with the number of seats per district,
    index of the list entry corresponds to the number of the district
    :param dist_merging: a list of values, each unique value is a new district
    and the main districts having the same value will be merged
    :return: the number and the fraction of votes obtained, and the number and the fraction of seats obtained, per party
    """
    seat_assignment = Counter()
    votes = Counter()

    # get the results for every district separately
    for new_dist in set(dist_merging):
        districts_to_merge = [dist for dist in range(len(dist_merging)) if dist_merging[dist] == new_dist]
        dist_seats = sum([seats_per_district[dist] for dist in districts_to_merge])

        new_dist_res = single_district_voting(voters.select(district_in=districts_to_merge), states=states,
                                              total_seats=dist_seats, assignment_func=assignment_func)
        seat_assignment += new_dist_res['seats']
        votes += new_dist_res['votes']

    # summation of counters above deletes the counts with value 0 from the result
    if states is not None:
        for party in states:
            if party not in seat_assignment:
                seat_assignment[party] = 0
            if party not in votes:
                votes[party] = 0

    vote_fractions = {party: Decimal(v) / Decimal(sum(votes.values())) for party, v in votes.items()}
    seat_fractions = {party: Decimal(s) / Decimal(total_seats) for party, s in seat_assignment.items()}

    # the final result is the aggregated result based on seats won in all districts
    return {'seat_fractions': seat_fractions, 'seats': seat_assignment, 'vote_fractions': vote_fractions,
            'votes': votes}


@apply_threshold
def mixed_voting(voters, states=None, total_seats=None, assignment_func=None, seats_per_district=None, **kw):
    """
    ------------ DEPRECATED ------------
    This function is currently not used, if you want to use it make necessary changes so it covers a desired case
    and include it in the Config.voting_systems dict.

    A very simple version of a mixed electoral system, which takes the results
    from single_district_voting and multi_district_voting and combines them
    in equal proportions by taking the average value of the seat share.
    :param voters: igraph.VertexSeq object, collection of voters  in the considered district with a 'state' parameter
    :param states: all possible states of voters (votes), should be provided in order to get the losers in the results
    :param total_seats: the total number of seats available in the district
    :param assignment_func: the function to use for assigning seats for parties
    :param seats_per_district: a list with the number of seats per district,
    index of the list entry corresponds to the number of the district
    :return: the number and the fraction of votes obtained, and the number and the fraction of seats obtained, per party
    """
    pop = single_district_voting(voters, states=states, total_seats=total_seats, assignment_func=assignment_func)
    dist = multi_district_voting(voters, states=states, total_seats=total_seats, assignment_func=assignment_func,
                                 seats_per_district=seats_per_district)

    seat_assignment = {}
    seat_fractions = {}
    for party in pop.keys():
        seat_assignment[party] = (pop['seats'] + dist['seats']) / Decimal('2')
        seat_fractions[party] = (pop['seat_fractions'] + dist['seat_fractions']) / Decimal('2')

    # compute the seats obtained globally based on the seats obtained in each system
    seat_assignment = assignment_func(total_seats, vote_fractions=seat_fractions,
                                      votes=seat_assignment, total_votes=sum(seat_assignment.values()))
    seat_fractions = {party: Decimal(s) / Decimal(total_seats) for party, s in seat_assignment.items()}

    return {'seat_fractions': seat_fractions, 'seats': seat_assignment, 'vote_fractions': pop['vote_fractions'],
            'votes': pop['votes']}


if __name__ == '__main__':
    # TODO move it to unit tests
    lst = [('a', 0), ('b', 0), ('b', 0), ('a', 0), ('a', 0), ('a', 1), ('a', 1),
           ('a', 1), ('c', 1), ('c', 1), ('b', 2), ('b', 2), ('b', 2), ('a', 2), ('c', 2), ('c', 2)]
    test_voters = [{'state': a, 'district': b} for a, b in lst]
    print(single_district_voting(test_voters, states=('a', 'b', 'c'), total_seats=3))
    print(multi_district_voting(test_voters, states=('a', 'b', 'c'), total_seats=3, seats_per_district=[1, 1, 1]))
    print(mixed_voting(test_voters, states=('a', 'b', 'c'), total_seats=3, seats_per_district=[1, 1, 1],
                       assignment_func=default_assignment))
