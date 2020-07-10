'''
Functions that model different election systems

mixed system: mix of population majority and district majority. 
The half of seats is allocated proportionally to population, the other half according to districts results.

TODO: explain more here
'''
import numpy as np
from itertools import groupby
from collections import Counter


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
    _max = counts[winner]
    winners = [w for w, v in counts.items() if v == _max]
    winner = np.random.choice(winners, 1)[0]
    fractions = Counter({k: 1.0 * v / total for k, v in counts.items()})
    # TODO: in 3-state model this does't add up to 1.0 due to floating point numbers arithmetics,
    #  decide either to ignore it or fix it with decimals
    # total = sum(fractions.values())
    # if total < 1.0:
    #     print('BBBBBBBBBBBBBBBBBBBBBBBBBBBBB :', str(total))
    return {'winner': winner, 'fractions': fractions}


# Extracts the vote from each individual voter and computes the winner based on the majority
def system_population_majority(voters):
    counts = {}
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
    voters_by_district = groupby(sorted(voters, key=extract_district), key=extract_district)
    results_by_district = {d: district_voting(vs) for d, vs in voters_by_district}
    counts = {}
    district_count = 0
    for district, res in results_by_district.items():
        winner = res['winner']
        if winner not in counts:
            counts[winner] = 0
        counts[winner] += 1
        district_count += 1
    return counts_to_result(counts, district_count)

# mixing results from system_population_majority and system_district_majority
def system_mixed(voters, district_voting=system_population_majority):
    pop = system_population_majority(voters)
    dist = system_district_majority(voters, district_voting=system_population_majority)
    result = pop['fractions'] + dist['fractions']
    for key in result:
        result[key] *= 0.5
    winner = max(result.keys(), key=result.get)
    return {'winner': winner, 'fractions': result}
    
# def run_voting_system(network, system=system_population_majority):
#     return system_population_majority(extract_voters(network))

# application of electoral threshold (minimal share of total votes to be considered at all)
def electoral_threshold(voters, threshold):
    if 0. < threshold <= 1.:
        results_without_threshold = system_population_majority(voters)['fractions']
        states_above_threshold = [state for state in results_without_threshold 
                                  if results_without_threshold[state] > threshold]
        #indexes of vertices which are above threshold
        voters_indexes = list(np.where(np.isin(voters['state'], states_above_threshold))[0])
        voters_above_threshold = voters[[int(item) for item in voters_indexes]] #have to use int instead of np.int64
        return voters_above_threshold
    else:
        return voters

if __name__ == '__main__':
    # This is some basic test code
    lst = [(1, 'a'), (-1, 'a'), (-1, 'a'), (1, 'b'), (1, 'b'), (1, 'b'), (1, 'b'), (-1, 'c'), (-1, 'c'), (1, 'c')]
    test_voters = [{'state': a, 'district': b} for a, b in lst]
    print(system_population_majority(test_voters))
    print(system_district_majority(test_voters))
