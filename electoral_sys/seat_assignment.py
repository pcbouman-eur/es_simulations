# -*- coding: utf-8 -*-
"""
This file contains functions assigning seats in a single district
based on election result in that district.
"""
import numpy as np
from math import floor
from decimal import Decimal

from configuration.logging import log


###########################################################
#                                                         #
#             Other seat assignment methods               #
#                                                         #
###########################################################


def hamilton_method(total_seats, vote_fractions=None, **kwargs):
    """
    This function starts with a floored assignment and keeps assigning seats to the
    party which has a fraction of seats with the greatest difference to their
    obtained fraction of votes, as in the Hamilton method.
    :param total_seats: total number of seats available in the district
    :param vote_fractions: fractions of votes gained in the district
    :return: seat assignment, a dict of a form {party_code: number_of_seats}
    """
    assignment = {party: floor(fraction * total_seats) for party, fraction in vote_fractions.items()}
    count = sum(assignment.values())
    diff = {party: assignment[party] - (total_seats * fraction) for party, fraction in vote_fractions.items()}

    while count < total_seats:
        # find the party with the biggest difference between seats assigned and the fraction of seats voted for
        worst_key = min(diff.keys(), key=lambda k: diff[k])
        _min = diff[worst_key]

        # if there is a draw, select a random single party (otherwise would be order-depending)
        worst_keys = [key for key, difference in diff.items() if difference == _min]
        worst_key = np.random.choice(worst_keys, 1)[0]

        # increase the number of seats for that party by 1 and see if all sits are assigned now
        assignment[worst_key] += 1
        count += 1
        diff[worst_key] = assignment[worst_key] - (total_seats * vote_fractions[worst_key])

    return assignment


def first_past_the_post(total_seats, vote_fractions=None, **kwargs):
    """
    This function assigns all seats to the party with the highest fraction of votes,
    as in the First Past The Post elections. Usually the total number of seats is 1
    in one district using FPTP, but there can be exceptions like electors
    in the US presidential election. If there is a draw, a random winner is chosen
    from among the best scores.
    :param total_seats: total number of seats available in the district
    :param vote_fractions: fractions of votes gained in the district
    :return: seat assignment, a dict of a form {party_code: number_of_seats}
    """
    assignment = {party: 0 for party, fraction in vote_fractions.items()}
    winners = [party for party, fraction in vote_fractions.items() if fraction == max(vote_fractions.values())]
    winner = np.random.choice(winners, 1)[0]
    assignment[winner] = total_seats
    return assignment


###########################################################
#                                                         #
#              Highest-averages methods                   #
#                                                         #
###########################################################


# TODO make a general Highest-averages methods function not to repeat stuff
def jefferson_method(total_seats, votes=None, **kwargs):
    """
    This function uses the Jefferson method for seat assignment,
    also known as the D’Hondt method or Hagenbach-Bischoff method.
    :param total_seats: total number of seats available in the district (int)
    :param votes: number of votes gained in the district by each party (dict)
    :return: seat assignment, a dict of a form {party_code: number_of_seats}
    """
    assignment = {party: 0 for party in votes.keys()}
    quotients = {party: Decimal(v) / (assignment[party] + 1) for party, v in votes.items()}

    while sum(assignment.values()) < total_seats:
        # find the party with the biggest quotient
        round_winner = max(quotients.keys(), key=lambda k: quotients[k])
        _max = quotients[round_winner]

        # if there is a draw, select a random single party (otherwise would be order-depending)
        round_winners = [key for key, quotient in quotients.items() if quotient == _max]
        round_winner = np.random.choice(round_winners, 1)[0]

        # increase the number of seats for that party by 1 and update the quotients
        assignment[round_winner] += 1
        quotients[round_winner] = votes[round_winner] / (assignment[round_winner] + 1)

    return assignment


# TODO tests
def webster_method(total_seats, votes=None, **kwargs):
    """
    This function uses the Webster method for seat assignment,
    also known as the Sainte-Laguë method, sometimes Schepers method.
    :param total_seats: total number of seats available in the district (int)
    :param votes: number of votes gained in the district by each party (dict)
    :return: seat assignment, a dict of a form {party_code: number_of_seats}
    """
    assignment = {party: 0 for party in votes.keys()}
    quotients = {party: Decimal(v) / (2 * assignment[party] + 1) for party, v in votes.items()}

    while sum(assignment.values()) < total_seats:
        # find the party with the biggest quotient
        round_winner = max(quotients.keys(), key=lambda k: quotients[k])
        _max = quotients[round_winner]

        # if there is a draw, select a random single party (otherwise would be order-depending)
        round_winners = [key for key, quotient in quotients.items() if quotient == _max]
        round_winner = np.random.choice(round_winners, 1)[0]

        # increase the number of seats for that party by 1 and update the quotients
        assignment[round_winner] += 1
        quotients[round_winner] = votes[round_winner] / (2 * assignment[round_winner] + 1)

    return assignment


# TODO tests
def modified_webster_method(total_seats, votes=None, **kwargs):
    """
    This function uses the modified Webster method for seat assignment,
    which starts with a divisor 1.4 instead of 1.
    :param total_seats: total number of seats available in the district (int)
    :param votes: number of votes gained in the district by each party (dict)
    :return: seat assignment, a dict of a form {party_code: number_of_seats}
    """
    assignment = {party: 0 for party in votes.keys()}
    quotients = {party: Decimal(v) / (2 * assignment[party] + Decimal('1.4')) for party, v in votes.items()}

    while sum(assignment.values()) < total_seats:
        # find the party with the biggest quotient
        round_winner = max(quotients.keys(), key=lambda k: quotients[k])
        _max = quotients[round_winner]

        # if there is a draw, select a random single party (otherwise would be order-depending)
        round_winners = [key for key, quotient in quotients.items() if quotient == _max]
        round_winner = np.random.choice(round_winners, 1)[0]

        # increase the number of seats for that party by 1 and update the quotients
        assignment[round_winner] += 1
        quotients[round_winner] = votes[round_winner] / (2 * assignment[round_winner] + 1)

    return assignment


# TODO tests
def imperiali_method(total_seats, votes=None, **kwargs):
    """
    This function uses the Imperiali highest-averages method for seat assignment
    (it's not the Imperiali quota which is a largest reminder method)
    :param total_seats: total number of seats available in the district (int)
    :param votes: number of votes gained in the district by each party (dict)
    :return: seat assignment, a dict of a form {party_code: number_of_seats}
    """
    assignment = {party: 0 for party in votes.keys()}
    quotients = {party: Decimal(v) / (assignment[party] + 2) for party, v in votes.items()}

    while sum(assignment.values()) < total_seats:
        # find the party with the biggest quotient
        round_winner = max(quotients.keys(), key=lambda k: quotients[k])
        _max = quotients[round_winner]

        # if there is a draw, select a random single party (otherwise would be order-depending)
        round_winners = [key for key, quotient in quotients.items() if quotient == _max]
        round_winner = np.random.choice(round_winners, 1)[0]

        # increase the number of seats for that party by 1 and update the quotients
        assignment[round_winner] += 1
        quotients[round_winner] = votes[round_winner] / (assignment[round_winner] + 2)

    return assignment


###########################################################
#                                                         #
#               Largest reminder methods                  #
#                                                         #
###########################################################


def largest_reminder_formula(quota, total_seats, votes):
    """
    General formula for the largest reminder seat assigning methods.
    After providing the proper quota it can compute the seat assigment
    under the methods like Hare quota, Droop quota, Imperiali quota etc.
    :param quota: the quota value corresponding to a given formula (Decimal)
    :param total_seats: total number of seats available in the district (int)
    :param votes: number of votes gained in the district by each party (dict)
    :return: seat assignment, a dict of a form {party_code: number_of_seats}
    """
    quotas = {party: v / quota for party, v in votes.items()}
    assignment = {party: floor(q) for party, q in quotas.items()}
    remainders = {party: q % 1 for party, q in quotas.items()}

    while sum(assignment.values()) < total_seats:
        largest_reminder = max(remainders.values())

        # if there is a draw, select a random single party (otherwise would be order-depending)
        lr_parties = [party for party, reminder in remainders.items() if reminder == largest_reminder]
        lr_party = np.random.choice(lr_parties, 1)[0]

        # add one of the remaining seats to this party and look for the next biggest reminder
        assignment[lr_party] += 1
        remainders.pop(lr_party)

    return assignment


def hare_quota(total_seats, votes=None, total_votes=None, **kwargs):
    """
    The Hare quota seat assigment method.
    :param total_seats: total number of seats available in the district (int)
    :param votes: number of votes gained in the district by each party (dict)
    :param total_votes: total number of votes casted (int)
    :return: seat assignment, a dict of a form {party_code: number_of_seats}
    """
    quota = Decimal(total_votes) / total_seats
    return largest_reminder_formula(quota, total_seats, votes)


def droop_quota(total_seats, votes=None, total_votes=None, **kwargs):
    """
    The (original) Droop quota seat assigment method, also called rounded Droop quota.
    :param total_seats: total number of seats available in the district (int)
    :param votes: number of votes gained in the district by each party (dict)
    :param total_votes: total number of votes casted (int)
    :return: seat assignment, a dict of a form {party_code: number_of_seats}
    """
    quota = Decimal(1 + floor(total_votes / (total_seats + 1)))
    return largest_reminder_formula(quota, total_seats, votes)


def exact_droop_quota(total_seats, votes=None, total_votes=None, **kwargs):
    """
    The exact Droop quota seat assigment method, also known as Hagenbach-Bischoff quota.
    In the rare case of assigning more seats than available it will use the (original) Droop quota.
    :param total_seats: total number of seats available in the district (int)
    :param votes: number of votes gained in the district by each party (dict)
    :param total_votes: total number of votes casted (int)
    :return: seat assignment, a dict of a form {party_code: number_of_seats}
    """
    quota = Decimal(total_votes) / (total_seats + 1)
    assignment = largest_reminder_formula(quota, total_seats, votes)
    if sum(assignment.values()) > total_seats:
        log.warning('The exact Droop quota assigned more seats than available! Increasing the quota to avoid it.')
        return droop_quota(total_seats, votes=votes, total_votes=total_votes)
    else:
        return assignment


def imperiali_quota(total_seats, votes=None, total_votes=None, **kwargs):
    """
    The Imperiali quota seat assigment method.
    In the case of assigning more seats than available it will use the exact Droop quota instead.
    :param total_seats: total number of seats available in the district (int)
    :param votes: number of votes gained in the district by each party (dict)
    :param total_votes: total number of votes casted (int)
    :return: seat assignment, a dict of a form {party_code: number_of_seats}
    """
    quota = Decimal(total_votes) / (total_seats + 2)
    assignment = largest_reminder_formula(quota, total_seats, votes)
    if sum(assignment.values()) > total_seats:
        log.warning('The Imperiali quota assigned more seats than available! Using the Droop quota.')
        return exact_droop_quota(total_seats, votes=votes, total_votes=total_votes)
    else:
        return assignment


# collection of seat-assigning functions that can be used in configuration (--seat_rule argument)
seat_assignment_rules = {
    'hamilton': hamilton_method,
    'jefferson': jefferson_method,
    'webster': webster_method,
    'modified_webster': modified_webster_method,
    'imperiali_average': imperiali_method,
    'hare': hare_quota,
    'droop': droop_quota,
    'exact_droop': exact_droop_quota,
    'imperiali_quota': imperiali_quota,
    'fptp': first_past_the_post,
}
