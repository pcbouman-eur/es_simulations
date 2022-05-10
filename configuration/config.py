# -*- coding: utf-8 -*-
"""
Contains a class an utilities that are used to store and access the
configuration of the simulation
"""
import sys
import json
import copy

import electoral_sys.electoral_system as es
from electoral_sys.seat_assignment import seat_assignment_rules
import net_generation.base as ng
import simulation.base as sim
from configuration.logging import log


class Config:
    """
    Holds the configuration of a simulation.

    :_cmd_args: a dict with command line arguments
    :voting_system: a voting system function used to determine the results of elections
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
    planar_c = None
    euclidean = None

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

    # main electoral systems which are computed in every simulation,
    # you can compute more by adding them in a configuration file under 'alternative_systems' parameter
    voting_systems = {
        # usually a proportional representation system which ignores districts
        # and assigns all seats based on the results in the whole country;
        # it can be, however, a first-past-the-post system with one district,
        # or majoritarian voting, if a proper seat allocation rule is provided
        'country-wide_system': es.single_district_voting,

        # a system with electoral districts as specified by 'district_sizes', either PR or first-past-the-post
        # what depends on the seat assignment method and number of seats per district,
        # it has the main parameters the same as the country-wide system (threshold, seat rule etc.)
        'main_district_system': es.multi_district_voting,
    }

    zealot_state = None
    not_zealot_state = None
    all_states = None  # the order matters in the mutation function! zealot first

    # alternative electoral systems can be passed only in the configuration file
    alternative_systems = None

    @staticmethod
    def wrap_configuration(voting_function, **kwargs):
        """
        A helper method to automatically provide configuration arguments to voting functions.
        :param voting_function: one of the voting functions from the electoral_system module
        :param kwargs: keyword arguments to be passed to the voting_function
        :return: a wrapped voting_function that now only needs voters (igraph.VertexSeq) as an argument
        """
        def inner(voters):
            return voting_function(voters, **kwargs)
        return inner

    @staticmethod
    def validate_threshold(threshold, param_path):
        """
        A function to validate the electoral threshold value provided in the configuration.
        :param threshold: (float) the threshold
        :param param_path: (string) from which part of the configuration is the threshold (for error message)
        :return: the threshold (float)
        """
        if threshold < 0 or threshold > 1:
            raise ValueError(f'The threshold should be in the range [0,1], '
                             f'threshold provided in {param_path} = {threshold}.')
        return threshold

    @staticmethod
    def validate_seats(seats, districts_num, param_path):
        """
        A function to validate seat numbers provided in the configuration
        and compute seats_per_district and total_seats.
        :param seats: (list of ints) the seats parameter provided in the configuration
        :param districts_num: (int) the number of electoral districts
        :param param_path: (string) from which part of the configuration is the parameter (for error message)
        :return: seats_per_district (list of ints with a length of districts_num), total_seats (int)
        """
        if len(seats) == 0:
            raise ValueError(f"No seats were provided in {param_path}.")
        elif len(seats) < districts_num:
            log.warning(f"There is fewer seat numbers specified than districts in {param_path}. "
                        "The seat numbers will be repeated.")
        elif len(seats) > districts_num:
            log.warning(f"There is more seat numbers specified than districts in {param_path}. "
                        "Not all seat numbers will be used.")
        seats_per_district = [seats[i % len(seats)] for i in range(districts_num)]
        total_seats = sum(seats_per_district)
        return seats_per_district, total_seats

    @staticmethod
    def validate_seat_rule(seat_rule, param_path):
        """
        A function to validate the seat_rule value provided in the configuration
        and find the corresponding seat assignment method.
        :param seat_rule: (string) the seat_rule parameter, it should be one of seat_assignment_rules.keys()
        :param param_path: (string) from which part of the configuration is the parameter (for error message)
        :return: seat allocation method (function)
        """
        try:
            seat_alloc_function = seat_assignment_rules[seat_rule]
        except KeyError:
            raise ValueError(f"The seat rule '{seat_rule}' provided in {param_path} does not exist, "
                             f"possible seat rules are: {[r for r in seat_assignment_rules.keys()]}")
        return seat_alloc_function

    def __init__(self, cmd_args, arg_dict):
        """
        Initialization of the configuration class with basic argument validation
        :param cmd_args: Namespace with command line arguments
        :param arg_dict: a private dict of the argparse parser to use only for parameters redundancy validation
        """
        # Read in the configuration file
        if cmd_args.config_file is not None:
            # types of values provided in the configuration file are not directly validated
            # (as the command line arguments are by the parser). Providing a wrong type, however, would for most cases
            # raise an error in the validation and parameter manipulation below. If this is not enough
            # one might think of using a data validation module like voluptuous in the future.
            config_file = json.load(cmd_args.config_file)
            log.info(f'Taking configuration from {cmd_args.config_file.name} file')

            # Parameters redundancy validation
            for argument in sys.argv[1:]:
                if argument[0] != '-':  # each command line arg starts with either '-' or '--', otherwise it's a value
                    continue
                try:
                    store_name = arg_dict[argument].dest
                except Exception:
                    raise Exception(f"Wrong command line argument '{argument}', this argument either does not exist, "
                                    "or it was provided in a different way than '--argument value' or '-a value', "
                                    "for example '--argument=value' will not work.")
                if store_name in config_file:
                    raise ValueError(f"Argument '{argument}' can not be provided in the command line and in the "
                                     f"configuration file ('{store_name}') simultaneously!")

            # Save the parameters, config file has the priority over command line arguments
            self._cmd_args = dict(vars(cmd_args), config_file=cmd_args.config_file.name, **config_file)
        else:
            # Save the parameters from the command line
            self._cmd_args = vars(cmd_args)  # config file has the priority

        cmd_args = None  # just to be sure that nobody will take any value from here

        # self._cmd_args is just to know what arguments the program was ran with
        # parameters should be taken directly from class Config attributes, because they are manipulated below
        for key, value in self._cmd_args.items():
            self.__setattr__(key, copy.deepcopy(value))

        # Filename suffix
        self.suffix = (f'_N_{self.n}_q_{self.q}_EPS_{self.epsilon}_S_{self.sample_size}_T_{self.therm_time}_'
                       f'MC_{self.mc_steps}_p_{self.propagation}_media_{self.mass_media}_zn_{self.n_zealots}')

        # Network structure
        if self.district_sizes is not None:
            if len(self.district_sizes) != self.q:
                raise ValueError(f"The list of district sizes (len={len(self.district_sizes)}) "
                                 f"must have a length equal to the number of districts (q={self.q})!")
            log.info('The network will be generated based on the district sizes')
            if self.n != sum(self.district_sizes):
                raise ValueError(f"The sum of district sizes (sum={sum(self.district_sizes)}) "
                                 f"must be equal to the size of the network (n={self.n})!")
        else:
            log.info('The network will be generated based on the number of districts and network size')
            if self.n % self.q != 0:
                raise ValueError('The number of nodes must be a multiplication of the number of districts!')
            one_district_size = self.n // self.q
            self.district_sizes = [one_district_size for _ in range(self.q)]

        if self.district_coords is not None:
            if len(self.district_coords) != self.q:
                raise ValueError(f"The list of district coordinates (len={len(self.district_coords)}) "
                                 f"must have a length equal to the number of districts (q={self.q})!")
            log.info('The network will have a "planar" structure based on district_coords and planar_c values')
            self.suffix += f"_gc_{self.planar_c}_c_{self.avg_deg}"
            if self.ratio is not None:
                log.warning('"ratio" parameter was provided, but will be ignored in the planar network')
        else:
            log.info('The network will have a simple planted block structure')
            self.suffix += f"_R_{self.ratio}_c_{self.avg_deg}"
            if self.planar_c is not None:
                log.warning('"planar_c" parameter was provided, but will be ignored in the simple planted network')

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
        else:
            self.all_states = generate_state_labels(self.num_parties)
            self.zealot_state = self.all_states[0]
            self.not_zealot_state = self.all_states[-1]
            self.suffix = ''.join(['_parties_', str(self.num_parties), self.suffix])

        if self.mass_media is None:
            self.mass_media = 1.0 / self.num_parties  # the symmetric case with no propaganda

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
        self.threshold = self.validate_threshold(self.threshold, 'the main configuration')
        if self.threshold != 0:
            self.suffix += f"_tr_{self.threshold}"

        # Seat allocation rules
        self.seats_per_district, self.total_seats = self.validate_seats(self.seats, self.q, 'the main configuration')
        self.seat_alloc_function = self.validate_seat_rule(self.seat_rule, 'the main configuration')

        # add the general configuration to the main pre-defined electoral systems
        for system in self.voting_systems.keys():
            self.voting_systems[system] = self.wrap_configuration(self.voting_systems[system], states=self.all_states,
                                                                  total_seats=self.total_seats,
                                                                  seats_per_district=self.seats_per_district,
                                                                  threshold=self.threshold,
                                                                  assignment_func=self.seat_alloc_function)

        # append the alternative systems
        if self.alternative_systems is not None:
            alt_names = []
            for alt in self.alternative_systems:
                # name and type are the very minimum that must be provided for each alternative system,
                # but with no more parameters specified it will be effectively the same as the 'main_district_system'
                if 'name' not in alt:
                    raise KeyError("One of the alternative systems is missing the 'name' value.")
                if 'type' not in alt:
                    raise KeyError(f"The alternative system '{alt['name']}' is missing the 'type' value.")

                if alt['name'] in alt_names:
                    raise ValueError(f"Alternative systems' names must be unique, '{alt['name']}' is repeated.")
                alt_names.append(alt['name'])

                # copy the basic parameters from the main configuration, if not provided
                alt['threshold'] = self.validate_threshold(alt.get('threshold', self.threshold),
                                                           f"alternative_systems/{alt['name']}")
                alt['seat_rule'] = alt.get('seat_rule', self.seat_rule)
                alt['seat_alloc_function'] = self.validate_seat_rule(alt['seat_rule'],
                                                                     f"alternative_systems/{alt['name']}")

                # in this type it is possible to change the seat_rule, seats, and threshold parameters,
                # but the number of districts and their sizes etc. stay the same as in the main configuration
                if alt['type'] == 'basic':
                    alt['seats'] = alt.get('seats', self.seats)
                    alt['seats_per_district'], alt['total_seats'] = self.validate_seats(
                        alt['seats'], self.q, f"alternative_systems/{alt['name']}")

                    self.voting_systems[alt['name']] = self.wrap_configuration(
                        es.multi_district_voting, states=self.all_states, total_seats=alt['total_seats'],
                        seats_per_district=alt['seats_per_district'], threshold=alt['threshold'],
                        assignment_func=alt['seat_alloc_function'])

                # in this system it is possible to change basic parameters plus to merge electoral districts
                elif alt['type'] == 'merge':
                    if 'dist_merging' not in alt or not isinstance(alt['dist_merging'], list) or len(
                            alt['dist_merging']) == 0:
                        raise KeyError(f"Alternative system '{alt['name']}': 'dist_merging' parameter must be provided "
                                       f"for a system of the type 'merge' and it must be a list indexes.")

                    # values in the list 'dist_merging' in configuration work as ids of new districts,
                    # i.e. districts with the same values will be merged
                    alt['q'] = len(set(alt['dist_merging']))

                    # this case serves for easy merging of all districts to have another country-wide system
                    if alt['q'] == 1:
                        if 'seats' in alt:
                            if len(alt['seats']) != 1:
                                raise ValueError(f"In the alternative system '{alt['name']}' len('seats')="
                                                 f"{len(alt['seats'])}, but there is only one district specified!")
                            alt['total_seats'] = alt['seats'][0]
                        else:
                            alt['total_seats'] = self.total_seats

                        self.voting_systems[alt['name']] = self.wrap_configuration(
                            es.single_district_voting, states=self.all_states, total_seats=alt['total_seats'],
                            threshold=alt['threshold'], assignment_func=alt['seat_alloc_function'])

                    # if alt['q']>1 then 'dist_merging' must provide a new id for each of the main districts
                    else:
                        if len(alt['dist_merging']) != self.q:
                            raise ValueError(f"In the alternative system '{alt['name']}' len('dist_merging')="
                                             f"{len(alt['dist_merging'])}, but there is {self.q} districts! The length "
                                             "of 'dist_merging' list must be equal to 1 or to the number of districts.")

                        alt['seats'] = alt.get('seats', self.seats)
                        # new seats must be provided for main districts and then they will be merged as well
                        alt['seats_per_district'], alt['total_seats'] = self.validate_seats(
                            alt['seats'], self.q, f"alternative_systems/{alt['name']}")

                        self.voting_systems[alt['name']] = self.wrap_configuration(
                            es.merged_districts_voting, states=self.all_states, total_seats=alt['total_seats'],
                            assignment_func=alt['seat_alloc_function'], seats_per_district=alt['seats_per_district'],
                            threshold=alt['threshold'], dist_merging=alt['dist_merging'])
                else:
                    raise NotImplementedError(f"Type '{alt['type']}' is not implemented, but was provided in the "
                                              f"configuration file for the alternative system '{alt['name']}'.")

        # short suffix in case of using a configuration file
        if self.config_file is not None:
            self.suffix = f'_{self.config_file[:-5]}_p_{self.propagation}_media_{self.mass_media}_zn_{self.n_zealots}'

        # at the end remove dots from the suffix so latex doesn't have issues with the filenames
        self.suffix = self.suffix.replace('.', '')


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
