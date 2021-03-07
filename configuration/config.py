# -*- coding: utf-8 -*-
"""
Contains a class an utilities that are used to store and access the
configuration of the simulation
"""
import sys
import json
import electoral_sys.electoral_system as es
from electoral_sys.seat_assignment import seat_assignment_rules
import net_generation.base as ng
import simulation.base as sim
from configuration.logging import log


class Config:
    """
    Holds the configuration of a simulation.

    :_cmd_args: a dict with command line arguments
    :voting_system: a voting system function used to determine a winner
    :initialize_states: a function that generates a vector of initial states
    :propagate: a function that propagates states from neighbours to a node
    :mutate: a function that changes the state of a node at random
    :zealot_state: the state of zealot nodes
    :not_zealot_state: the state taken as the opposition of the zealot state
    :all_states: all possible states of the nodes
    :zealots_config: configuration for the zealot initialization
    :suffix: suggested file name suffix for output files

    The rest of attributes are simply arguments defined in parser.py and described there
    """
    # parsed arguments that have default value defined in parser.py
    n = None
    q = None
    avg_deg = None
    ratio = None
    district_sizes = None
    district_coords = None
    p_norm = None
    planar_c = None

    seats = None
    seat_rule = None
    threshold = None

    sample_size = None
    therm_time = None
    mc_steps = None
    reset = None
    random_dist = None
    consensus = None

    n_zealots = None
    where_zealots = None
    zealots_district = None
    mass_media = None

    epsilon = None
    propagation = None
    num_parties = None

    config_file = None

    # derivatives of parsed arguments and others
    initialize_states = staticmethod(ng.default_initial_state)
    propagate = staticmethod(sim.default_propagation)
    mutate = staticmethod(sim.default_mutation)

    voting_systems = {
        'population': es.system_population_majority,  # the idealised proportional representation, ignores districts
        'district': es.system_district_majority,  # a system with districts, either PR or first-past-the-post
                                                  # depends on the seat assignment method
        'mixed': es.system_mixed,  # a dummy mixed system mixing seats from two others in equal proportions
    }

    zealot_state = 'a'
    not_zealot_state = 'b'
    all_states = ('a', 'b')  # the order matters in the mutation function! zealot first

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
            self._cmd_args = dict(vars(cmd_args), config_file=cmd_args.config_file.name,
                                  **config_file)  # config file has the priority
        else:
            # Command line arguments
            self._cmd_args = vars(cmd_args)  # config file has the priority

        cmd_args = None  # just to be sure that nobody will take any value from here

        # self._cmd_args is just to know what arguments the program was ran with
        # parameters should be taken directly from class Config attributes, because they are manipulated below
        for key, value in self._cmd_args.items():
            self.__setattr__(key,  value)

        # Filename suffix
        self.suffix = (f'_N_{self.n}_q_{self.q}_EPS_{self.epsilon}_S_{self.sample_size}_T_{self.therm_time}_'
                       f'MC_{self.mc_steps}_p_{self.propagation}_media_{self.mass_media}_zn_{self.n_zealots}')
        self.suffix = self.suffix.replace('.', '')

        # Network structure
        if self.district_sizes is not None:
            if len(self.district_sizes) != self.q:
                raise ValueError(f"The list of district sizes (len={len(self.district_sizes)}) "
                                 f"must have length equal to the number of districts (q={self.q})!")
            log.info('The network will be generated based on the district sizes')
            self.n = sum(self.district_sizes)
        else:
            log.info('The network will be generated based on the number of districts and network size')
            if self.n % self.q != 0:
                raise ValueError('The number of nodes must be a multiplication of the number of districts!')
            one_district_size = self.n // self.q
            self.district_sizes = [one_district_size for _ in range(self.q)]
        if self.district_coords is not None:
            if len(self.district_coords) != self.q:
                raise ValueError(f"The list of district coordinates (len={len(self.district_coords)}) "
                                 f"must have length equal to the number of districts (q={self.q})!")
            log.info('The network will be have a "planar" structure')
            self.suffix += f"_graph_planar_gp_{self.p_norm}_gc_{self.planar_c}_c_{self.avg_deg}"
        else:
            log.info('The network will be have a simple planted block structure')
            self.suffix += f"_graph_sbm_R_{self.ratio}_c_{self.avg_deg}"

        # Propagation mechanisms
        if self.propagation == 'majority':
            self.propagate = sim.majority_propagation
        elif self.propagation == 'minority':
            def f(n, g):
                return sim.majority_propagation(n, g, True)
            self.propagate = f

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
        if self.where_zealots == 'degree':
            self.zealots_config = {'degree_driven': True,
                                   'one_district': False,
                                   'district': None}
        elif self.where_zealots == 'district':
            self.zealots_config = {'degree_driven': False,
                                   'one_district': True,
                                   'district': self.zealots_district}
        else:
            self.zealots_config = {'degree_driven': False,
                                   'one_district': False,
                                   'district': None}
        
        # Electoral threshold
        if self.threshold < 0 or self.threshold > 1:
            raise ValueError(f'The threshold should be in the range [0,1], '
                             f'current threshold = {self.threshold}.')
        elif self.threshold == 0:
            pass  # for threshold == 0 we do not consider thresholding
        else:
            self.suffix += f"_tr_{self.threshold}"

        # Seat allocation rules
        if len(self.seats) < self.q:
            log.warning("There is fewer seat numbers specified than districts in the network. "
                        "The seat numbers will be repeated.")
        elif len(self.seats) > self.q:
            log.warning("There is more seat numbers specified than districts in the network. "
                        "Not all seat numbers will be used.")
        self.seats_per_district = [self.seats[i % len(self.seats)] for i in range(self.q)]
        self.total_seats = sum(self.seats_per_district)
        self.seat_alloc_function = seat_assignment_rules[self.seat_rule]


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
