# -*- coding: utf-8 -*-
"""
This file contains functions assigning seats in a single district
based on election result in that district.
"""
import numpy as np
from math import floor


def simple_rule(total_seats, fractions):
    """
    This function starts with a floored assignment and keeps assigning seats to the
    party which has a fraction of seats with the greatest difference to their
    obtained fraction of votes.
    :param total_seats: total number of seats available in the district
    :param fractions: fractions of votes gained in the district
    :return: seat assignment, a dict of a form {party_code: number_of_seats}
    """
    assignment = {party: floor(fraction * total_seats) for party, fraction in fractions.items()}
    count = sum(assignment.values())
    diff = {party: assignment[party] - (total_seats * fraction) for party, fraction in fractions.items()}

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
        diff[worst_key] = assignment[worst_key] - (total_seats * fractions[worst_key])

    return assignment


def jefferson_method(total_seats, fractions):
    """
    This function uses the Jefferson method for seat assignment
    (also known as the D’Hondt method or Hagenbach-Bischoff method).
    Originally it is defined for the numbers of votes, not fractions of votes,
    but using fractions doesn't change the result, just normalizes the calculations.
    :param total_seats: total number of seats available in the district
    :param fractions: fractions of votes gained in the district
    :return: seat assignment, a dict of a form {party_code: number_of_seats}
    """
    assignment = {party: 0 for party, fraction in fractions.items()}
    quotients = {party: fraction / (assignment[party] + 1) for party, fraction in fractions.items()}

    while sum(assignment.values()) < total_seats:
        # find the party with the biggest quotient
        round_winner = max(quotients.keys(), key=lambda k: quotients[k])
        _max = quotients[round_winner]

        # if there is a draw, select a random single party (otherwise would be order-depending)
        round_winners = [key for key, quotient in quotients.items() if quotient == _max]
        round_winner = np.random.choice(round_winners, 1)[0]

        # increase the number of seats for that party by 1 and update the quotients
        assignment[round_winner] += 1
        quotients[round_winner] = fractions[round_winner] / (assignment[round_winner] + 1)

    return assignment


# collection of seat-assigning functions that can be used in configuration (--seat_rule argument)
seat_assignment_rules = {
    'default': simple_rule,
    'jefferson': jefferson_method,
    'dhondt': jefferson_method,
}
