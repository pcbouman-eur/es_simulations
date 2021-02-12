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


# collection of seat-assigning functions that can be used in configuration (--seat_rule argument)
seat_assignment_rules = {'default': simple_rule}
