# -*- coding: utf-8 -*-
"""
Functions used to model different election systems and apply them to the distributions of voters
"""
import numpy as np
from decimal import Decimal
from itertools import groupby
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
            res_without_threshold = system_population_majority(voters, *args, **kwargs)['fractions']

            # indexes of vertices which are above threshold, using Decimal for exact comparision
            new_voters = voters.select(lambda voter: res_without_threshold[voter['state']] >= Decimal(str(threshold)))

            # check if any party has made it above the threshold to avoid issues
            if len(new_voters) > 0:
                voters = new_voters
            else:
                # this shouldn't happen in reasonable scenarios
                log.warning('No party has reached the entry threshold, so the threshold is being ignored')

        return system_func(voters, *args, **kwargs)

    return inner


###########################################################
#                                                         #
#                  Helper functions                       #
#                                                         #
###########################################################

def counts_to_result(counts, total):
    """
    Convenience function that produces the outcome of an election
    in one district based on counts per option.
    :param counts: a dict with a number of counts (votes/seats) for every option
    :param total: the total number of votes/seats, i.e. the normalization factor
    :return: the winner and the fractions of votes/seats obtained
    """
    # find the party with maximal number of votes
    winner = max(counts.keys(), key=counts.get)
    _max = counts[winner]

    # if there is a draw, select a random single winner
    winners = [party for party, votes in counts.items() if votes == _max]
    winner = np.random.choice(winners, 1)[0]

    # compute the fraction of all votes obtained by parties
    fractions = Counter({party: Decimal(votes) / Decimal(total) for party, votes in counts.items()})

    return {'winner': winner, 'fractions': fractions}


###########################################################
#                                                         #
#                 Electoral systems                       #
#                                                         #
###########################################################

@apply_threshold
def system_population_majority(voters, states=None, total_seats=None, assignment_func=None, **kwargs):
    """
    Extracts the vote from each individual voter and computes the winner based on the maximal score,
    computes the fraction of votes obtained, and the number of seats obtained in the considered district.
    :param voters: collection of voters with 'state' and 'district' parameters
    :param states: all possible states of voters (votes), should be provided in order to get the losers in the results
    :param total_seats: the total number of seats available in the district
    :param assignment_func: the function to use for assigning seats for parties
    :return: the winner, the fractions of votes obtained, and the number of seats obtained, per party/state
    """
    counts = {}
    if states is not None:
        for state in states:
            counts[state] = 0

    # counting manually, because 'voters' can be an object without len attribute
    voter_count = 0

    # count the votes for every state/party
    for voter in voters:
        voter_count += 1
        vote = voter['state']

        if vote not in counts:
            counts[vote] = 1
        else:
            counts[vote] += 1

    res = counts_to_result(counts, voter_count)

    # compute the seats obtained within the considered district
    if assignment_func is None:
        log.error("Seat assignment rule was not specified! Using default_assignment")
        assignment_func = default_assignment
    seat_assignment = Counter(assignment_func(total_seats, res['fractions']))

    return dict(res, seats=seat_assignment)


@apply_threshold
def system_district_majority(voters, district_voting=system_population_majority, states=None, total_seats=None,
                             seats_per_district=None, assignment_func=None):
    """
    Applies a voting system to each district, and then aggregates votes based on the
    seats won in each district.
    :param voters: collection of voters with 'state' and 'district' parameters, igraph.VertexSeq object
    :param district_voting: function calculating election result for a single district
    :param states: all possible states of voters (votes), should be provided in order to get the losers in the results
    :param total_seats: the total number of seats available in all districts together
    :param seats_per_district: a list with the number of seats per district,
    index of the list entry corresponds to the number of the district
    :param assignment_func: the function to use for assigning seats for parties
    :return: the winner, the fractions of votes obtained, and the number of seats obtained, per party/state
    """
    # get the results for every district separately, ultimately only seats matter;
    # in normal circumstances voters are already sorted according to their district,
    # but not always, e.g. not for parameter --random_districts, and then sorting is necessary
    voters_by_district = groupby(sorted(voters, key=lambda v: v['district']), key=lambda v: v['district'])
    seats = Counter()
    for district, dist_voters in voters_by_district:
        seats += district_voting(dist_voters, states=states, total_seats=seats_per_district[district],
                                 assignment_func=assignment_func)['seats']

    # summation of counters above deletes the counts with value 0 from the result
    if states is not None:
        for state in states:
            if state not in seats:
                seats[state] = 0

    # the final result is the aggregated result based on seats won in all districts
    return dict(counts_to_result(seats, total_seats), seats=seats)


@apply_threshold
def system_mixed(voters, district_voting=system_population_majority, states=None, total_seats=None,
                 seats_per_district=None, assignment_func=None):
    """
    Simple version of a mixed electoral system, which takes the results
    from system_population_majority and system_district_majority and combines them
    in equal proportions.
    :param voters: collection of voters with 'state' and 'district' parameters, igraph.VertexSeq object
    :param district_voting: function calculating election result for a single district
    :param states: all possible states of voters (votes), should be provided in order to get the losers in the results
    :param total_seats: the total number of seats available in all districts together
    :param seats_per_district: a list with the number of seats per district,
    index of the list entry corresponds to the number of the district
    :param assignment_func: the function to use for assigning seats for parties
    :return: the winner, the fractions of votes obtained, and the number of seats obtained, per party/state
    """
    pop = system_population_majority(voters, states=states, total_seats=total_seats, assignment_func=assignment_func)
    dist = system_district_majority(voters, district_voting=district_voting, states=states, total_seats=total_seats,
                                    seats_per_district=seats_per_district, assignment_func=assignment_func)

    # virtually there are two non-integer votes - one from the first system, and one from the second system
    res = counts_to_result(pop['fractions'] + dist['fractions'], 2)

    # compute the seats obtained globally based on the fraction of votes
    seat_assignment = Counter(assignment_func(total_seats, res['fractions']))

    # mixed system is the only one that can lack a party in result['seats'], if the party gained 0 seats
    # it's due to adding counters: pop['fractions'] + dist['fractions'] :if it's a problem change it
    return dict(res, seats=seat_assignment)


if __name__ == '__main__':
    # TODO move it to unit tests
    lst = [('a', 0), ('b', 0), ('b', 0), ('a', 0), ('a', 0), ('a', 1), ('a', 1),
           ('a', 1), ('c', 1), ('c', 1), ('b', 2), ('b', 2), ('b', 2), ('a', 2), ('c', 2), ('c', 2)]
    test_voters = [{'state': a, 'district': b} for a, b in lst]
    print(system_population_majority(test_voters, states=('a', 'b', 'c'), total_seats=3))
    print(system_district_majority(test_voters, states=('a', 'b', 'c'), total_seats=3, seats_per_district=[1, 1, 1]))
    print(system_mixed(test_voters, states=('a', 'b', 'c'), total_seats=3, seats_per_district=[1, 1, 1],
                       assignment_func=default_assignment))
