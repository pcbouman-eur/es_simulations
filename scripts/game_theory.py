import random
from math import tanh
import numpy as np
from matplotlib import pylab as plt

# Constants for the two choices players can make in a game
A = 0
B = 1


def init_states(n, value=None):
    """
    Initializes a state list for twice the number of agents, so we are
    always able to make pairs
    :param n: half the number of agents to generate
    :param value: the initial value to generate. If it is None (default),
                  each agent gets a random value in [0,1)
    """
    if value is None:
        return [random.random() for _ in range(2*n)]
    return [value for _ in range(2*n)]


def payoff_matrix(delta, d_a, d_b):
    """
    Gives a dictionary that represents a payoff matrix in the game
    :param delta: the value $\Delta$ in the structure of the game
    :param d_a: the value $\delta_a$ in the structure of the game
    :param d_b: the value $\delta_b$ int he structure of the game
    :result: a dictionary representing the payoff matrix
    """
    if d_a < 0 or d_a > delta:
        raise ValueError('The assumption 0 <= d_a <= delta is violated')
    if d_b < 0 or d_b > delta:
        raise ValueError('The assumption 0 <= d_b <= delta is violated')
    return { (A,A) : delta,
             (A,B) : -d_b,
             (B,A) : -d_a,
             (B,B) : delta}


def play_game(a1, a2, payoff_matrix):
    """
    Computes the choices of two players and provides the payoffs for both
    players as they are given in the provided payoff matrix
    :param a1: the probability that the first player chooses A
    :param a2: the probability that the second player chooses B
    :param payoff_matrix: a dictionary that contains the payoffs
    :result: a tuple containing the payoffs for both players
    """
    choice1 = A if random.random() <= a1 else B
    choice2 = A if random.random() <= a2 else B
    payoff1 = payoff_matrix[(choice1, choice2)]
    payoff2 = payoff_matrix[(choice2, choice1)]
    return payoff1, payoff2


def update_function(x, constant):
    """
    The update function f as given in the game theory document.
    Since A was already used to represent the choice A of a player, it was
    named constants in the function
    :param x: the input of the update function
    :param constant: the constant called A in the formula in the document
    :result: the output of the function
    """
    return 0.5 * (1 + tanh(constant * (x-0.5)))


def compute_new_probability(a_old, payoff, constant):
    """
    Computes the new probability that a player plays A given their
    old probability to play A and the payoff in a game outcome.
    :param a_old: the old probability to play A
    :param payoff: the payoff the player received
    :param constant: the constant used by the update function
    :result: the new probability to play A
    """
    # TODO: replace constant by the function for more general code?
    return update_function(a_old + payoff, constant)


def simulate(n, rounds, payoff_matrix, constant, init_value=None):
    """
    Runs a simulation based on the game theory idea
    :param n: half the number of agents (to make sure there is an even number)
    :param rounds: the number of rounds to repeat the simulation
    :param payoff_matrix: the payoff matrix given as dictionary
    :param constant: the constant to use in the payoff function
    :param init_value: the initial probability of the players (None is random)
    :result: the states of the players and the expected outcome of the states
    """
    indices = [i for i in range(2*n)]
    states = init_states(n, value=init_value)
    result = np.zeros((2*n,rounds))
    expected = np.zeros(rounds)
    for rnd in range(rounds):
        random.shuffle(indices)
        for i in range(0,2*n,2):
            idx1 = indices[i]
            idx2 = indices[i+1]
            a1 = states[idx1]
            a2 = states[idx2]
            payoff1, payoff2 = play_game(a1, a2,payoff_matrix)
            a1new = compute_new_probability(a1, payoff1, constant)
            a2new = compute_new_probability(a2, payoff2, constant)
            states[idx1] = a1new
            states[idx2] = a2new
        result[:,rnd] = states
        expected[rnd] = sum(states) / len(states)
    return result, expected


# Some model settings
players_half = 5
rounds = 20
constant = 1
pm = payoff_matrix(0.2,0.15,0.05)
init_value = None # This gives a random starting state to each player
# Run the simulation
results, expected = simulate(players_half, rounds, pm, constant,
                            init_value=init_value)
# Make a plot containing a single line for each player
for row in results:
    plt.plot(row, linewidth=0.3, alpha=0.7)
# Plot a thicker line line with the average outcome in each round
plt.plot(expected, linewidth=2)
# Fix the y-axis
plt.ylim([0,1])
plt.show()


