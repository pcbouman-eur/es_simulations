# -*- coding: utf-8 -*-
"""
Contains a class an utilities that are used to store and access the
configuration of the simulation
"""
import sys
import json
import electoral_sys.electoral_system as es
import net_generation.base as ng
import simulation.base as sim
from configuration.logging import log


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
    zealot_state = 'a'
    not_zealot_state = 'b'
    all_states = ('a', 'b')  # the order matters in the mutation function! zealot first
    reset = False
    consensus = False
    random_dist = False
    num_parties = 2

    def __init__(self, cmd_args, arg_dict):
        """
        Initialization of the configuration class with basic argument validation
        :param cmd_args: Namespace with command line arguments
        :param arg_dict: a private dict of the argparse parser to use only for parameters redundancy validation
        """
        # Read in the configuration file
        if cmd_args.config_file is not None:
            config_file = json.load(cmd_args.config_file)
            log.info(f'Taking configuration from {cmd_args.config_file.name} file')
        else:
            config_file = dict()

        # Parameters redundancy validation
        for argument in sys.argv[1:]:
            if argument[0] != '-':  # each command line arg starts with either '-' or '--', otherwise it's a value
                continue
            try:
                store_name = arg_dict[argument].dest
            except Exception:
                raise Exception("This shouldn't happen...")
            if store_name in config_file:
                raise ValueError(f"Argument '{argument}' can not be provided in the command line and in the "
                                 f"configuration file ('{store_name}') simultaneously!")

        # Command line arguments
        self.cmd_args = dict(vars(cmd_args),
                             config_file=cmd_args.config_file.name,
                             **config_file)  # config file has the priority
        cmd_args = None  # just to be sure that nobody will take any value from here
        self.reset = self.cmd_args['reset']
        self.consensus = self.cmd_args['consensus']
        self.random_dist = self.cmd_args['random_dist']
        self.num_parties = self.cmd_args['num_parties']

        # Network structure
        if self.cmd_args['district_sizes'] is not None:
            self.district_sizes = self.cmd_args['district_sizes']
            if len(self.district_sizes) != self.cmd_args['q']:
                raise ValueError(f"The list of district sizes (len={len(self.district_sizes)}) "
                                 f"must have a length equal to the number of districts (q={self.cmd_args['q']})!")
            log.info('The network will be generated based on the district sizes')
            self.cmd_args['N'] = sum(self.district_sizes)
        else:
            log.info('The network will be generated based on the number of districts and network size')
            if self.cmd_args['N'] % self.cmd_args['q'] != 0:
                raise ValueError('The number of nodes must be a multiplication of the number of districts!')
            one_district_size = self.cmd_args['N'] // self.cmd_args['q']
            self.district_sizes = [one_district_size for _ in range(self.cmd_args['q'])]

        # Propagation mechanisms
        if self.cmd_args['propagation'] == 'majority':
            self.propagate = sim.majority_propagation
        elif self.cmd_args['propagation'] == 'minority':
            def f(n, g):
                return sim.majority_propagation(n, g, True)
            self.propagate = f

        # Filename suffix
        self.suffix = '_N_{N}_q_{q}_EPS_{EPS}_S_{SAMPLE_SIZE}_T_{THERM_TIME}_MC_{mc_steps}_R_{ratio}' \
                      '_c_{avg_deg}_p_{propagation}_media_{MASS_MEDIA}_zn_{n_zealots}'.format_map(self.cmd_args)
        self.suffix = self.suffix.replace('.', '')

        # Determine the number of states
        if self.num_parties < 2:
            raise ValueError('The simulation needs at least two states')
        if self.num_parties > 2:
            self.all_states = generate_state_labels(self.num_parties)
            self.not_zealot_state = self.all_states[-1]
            self.suffix = ''.join(['_parties_', str(self.num_parties), self.suffix])

        # Initialization in the consensus state
        if self.consensus:
            self.initialize_states = ng.consensus_initial_state

        # Zealot configuration options
        if self.cmd_args['where_zealots'] == 'degree':
            self.zealots_config = {'degree_driven': True,
                                   'one_district': False,
                                   'district': None}
        elif self.cmd_args['where_zealots'] == 'district':
            self.zealots_config = {'degree_driven': False,
                                   'one_district': True,
                                   'district': self.cmd_args['zealots_district']}
        else:
            self.zealots_config = {'degree_driven': False,
                                   'one_district': False,
                                   'district': None}
        
        # Electoral threshold
        self.threshold = self.cmd_args['threshold']
        if self.threshold < 0. or self.threshold > 1.:
            raise ValueError(f'The threshold should be in the range [0,1], '
                             f'current threshold = {self.threshold}.')
        elif self.threshold == 0.:
            pass  # for threshold == 0 we do not consider thresholding
        else:
            self.suffix += f"_tr_{self.threshold}"

        # Seat allocation rules
        seats = self.cmd_args['seats']
        self.seats_per_district = [seats[i % len(seats)] for i in range(self.cmd_args['q'])]
        self.seat_rounding_rule = self.cmd_args['seatrule']
        if len(seats) < self.cmd_args['q']:
            log.warning("There is fewer seat numbers specified than districts in the network. "
                        "The seat numbers will be repeated.")
        elif len(seats) > self.cmd_args['q']:
            log.warning("There is more seat numbers specified than districts in the network. "
                        "Not all seat numbers will be used.")


def num_to_chars(n):
    """
    Converts a number into a alphabetic label, with support for labels beyond 26.
    I.e., 0 is converted to a, 1 to b, 26 to aa, 27 to ab, etcetera.
    :param n: the number to convert to an alphabetic label
    :return: string, a number converted to a label
    """
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


def generate_state_labels(n):
    """
    Generates an alphabetic list of labels in a sequence. For example, if three
    labels must be generated, the output will be ['a', 'b', 'c']
    :param n: the number of labels to generate
    :return: list of strings with labels
    """
    return [num_to_chars(i) for i in range(n)]
