from math import floor

# This starts with a floored assignment and keeps assigning seats to the
# party which has a fraction of seats with the greatest difference to their
# obtained fraction of votes
def default_rule(seats, fractions):
    assignment = {k: floor(f*seats) for k,f in fractions.items()}
    count = sum(assignment.values())
    diff = {k : assignment[k] - (seats * f) for k,f in fractions.items()}
    while (count < seats):
        worst_key = min(diff.keys(), key=lambda k:diff[k])
        assignment[worst_key] += 1
        count += 1
        diff[worst_key] = assignment[worst_key] - (seats * fractions[worst_key])
    return assignment


seat_assignment_rule_names = ['default']