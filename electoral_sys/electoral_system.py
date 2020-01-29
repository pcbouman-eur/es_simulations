'''
Functions that model different election systems

TODO: explain more here
'''

from itertools import groupby


# Retrieve the voters from a network
def extract_voters(network):
    return network.vs


# Retrieve the vote of a voter
def extract_vote(voter):
    return voter['state']


# Retrieve the district of a voter
def extract_district(voter):
    return voter['district']


# Convenience function that produces the outcome of an election based on counts per option
def counts_to_result(counts, total):
    winner = max(counts.keys(), key=counts.get)
    fractions = {k: v / total for k, v in counts.items()}
    return {'winner': winner, 'fractions': fractions}


# Extracts the vote from each individual voter and computes the winner based on the majority
def system_population_majority(voters):
    counts = {1: 0, -1: 0}
    voter_count = 0
    for voter in voters:
        vote = extract_vote(voter)
        if vote not in counts:
            counts[vote] = 0
        counts[vote] += 1
        voter_count += 1
    return counts_to_result(counts, voter_count)


# Applies a voting system to each district, and then aggregates votes based on the
# winner of each district
def system_district_majority(voters, district_voting=system_population_majority):
    voters_by_district = groupby(voters, extract_district)
    results_by_district = {d: district_voting(vs) for d, vs in voters_by_district}
    counts = {1: 0, -1: 0}
    district_count = 0
    for district, res in results_by_district.items():
        winner = res['winner']
        if winner not in counts:
            counts[winner] = 0
        counts[winner] += 1
        district_count += 1
    return counts_to_result(counts, district_count)


def run_voting_system(network, system=system_population_majority):
    return system_population_majority(extract_voters(network))


if __name__ == '__main__':
    # This is some basic test code
    lst = [(1, 'a'), (-1, 'a'), (-1, 'a'), (1, 'b'), (1, 'b'), (1, 'b'), (1, 'b'), (-1, 'c'), (-1, 'c'), (1, 'c')]
    test_voters = [{'state': a, 'district': b} for a, b in lst]
    print(system_population_majority(test_voters))
    print(system_district_majority(test_voters))
