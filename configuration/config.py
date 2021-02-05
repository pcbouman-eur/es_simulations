"""
Contains a class an utilities that are used to store and access the
configuration of the simulation
"""

import electoral_sys.electoral_system as es
import net_generation.base as ng
import simulation.base as sim


class Config:
    """
    Holds the configuration of a simulation.

    :cmd_args: an argparse Namespace with command line arguments
    :voting_system: a voting system function used to determine a winner
    :initialize_states: a function that generates a vector of initial states
    :propagate: a function that propagates states from neighbours to a node
    :mutate: a function that changes the state of a node at random
    :reset: whether to generate new initial states after each simulation
    :zealots_config: configuration for the zealot initialization
    :suffix: suggested file name suffix for output files
    """

    initialize_states = staticmethod(ng.default_initial_state)
    voting_systems = {'population': es.system_population_majority,
                      'district': es.system_district_majority,
                      'mixed': es.system_mixed}
    propagate = staticmethod(sim.default_propagation)
    mutate = staticmethod(sim.default_mutation)
    zealot_state = 1
    not_zealot_state = -1
    all_states = (1, -1)  # the order matters in the mutation function! zealot first
    reset = False
    consensus = False
    random_dist = False
    num_parties = 2

    def __init__(self, cmd_args):
        # Command line arguments
        self.cmd_args = cmd_args
        self.reset = cmd_args.reset
        self.consensus = cmd_args.consensus
        self.random_dist = cmd_args.random_dist
        self.num_parties = cmd_args.num_parties

        # Propagation mechanisms
        if cmd_args.propagation == 'majority':
            self.propagate = sim.majority_propagation
        elif cmd_args.propagation == 'minority':
            def f(n, g):
                return sim.majority_propagation(n, g, True)
            self.propagate = f

        # Filename suffix
        self.suffix = '_N_{N}_q_{q}_EPS_{EPS}_S_{SAMPLE_SIZE}_T_{THERM_TIME}_MC_{mc_steps}_R_{ratio}' \
                      '_c_{avg_deg}_p_{propagation}_media_{MASS_MEDIA}_zn_{n_zealots}'.format_map(vars(cmd_args))
        self.suffix = self.suffix.replace('.', '')

        # Deteermine the number of states
        if self.num_parties < 2:
            raise ValueError('The simulation needs at least two states')
        if self.num_parties > 2:
            self.all_states = generate_state_labels(self.num_parties)
            self.zealot_state = self.all_states[0]
            self.not_zealot_state = self.all_states[-1]
            self.suffix = ''.join(['_parties_'+str(self.num_parties), self.suffix])


        # # 3 states version of the model (abc)
        # if self.abc:
        #     self.zealot_state = 'a'
        #     self.not_zealot_state = 'c'
        #     self.all_states = ('a', 'b', 'c')  # the order matters in the mutation function!
        #     self.suffix = ''.join(['_abc', self.suffix])

        # initialization in the consensus state
        if self.consensus:
            self.initialize_states = ng.consensus_initial_state

        # Zealot configuration options
        if cmd_args.where_zealots == 'degree':
            self.zealots_config = {'degree_driven': True,
                                   'one_district': False,
                                   'district': None}
        elif cmd_args.where_zealots == 'district':
            self.zealots_config = {'degree_driven': False,
                                   'one_district': True,
                                   'district': cmd_args.zealots_district}
        else:
            self.zealots_config = {'degree_driven': False,
                                   'one_district': False,
                                   'district': None}
        
        # Electoral threshold
        self.threshold = cmd_args.threshold
        if self.threshold < 0. or self.threshold > 1.:
            raise ValueError(f'The threshold should be in the range [0,1], \
                             current threshold = {self.threshold}.')
        elif self.threshold == 0.:
            pass  # for threshold == 0 we do not consider thresholding
        else:
            self.suffix += f"_tr_{self.threshold}"

        # Seat allocation rules
        seats = cmd_args.seats
        self.seats_per_district = [seats[i % len(seats)] for i in range(cmd_args.q)]
        self.seat_rounding_rule = cmd_args.seatrule


"""
Converts a number into a alphabetic label, with support for labels beyond 26.
I.e., 0 is converted to a, 1 to b, 26 to aa, 27 to ab, etcetera.

:n: the number to convert to an alphabetic label
"""
def num_to_chars(n):
    if not isinstance(n, int) or n < 0:
        raise ValueError('Only a non-negative integer is supported')
    first_char = 97
    alphabet_length = 26
    result = ''
    while True:
        result += chr(first_char + n % alphabet_length)
        if n >= alphabet_length:
            n = n // alphabet_length - 1
        else:
            break
    return result[::-1]

"""
Generates an alphabetic list of labels in a sequence. For example, if three
labels must be generated, the output will be ['a', 'b', 'c']

:n: the number of labels to generate
"""
def generate_state_labels(n):
    return [num_to_chars(i) for i in range(n)]
