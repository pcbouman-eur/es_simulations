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
                      'district': es.system_district_majority}
    propagate = staticmethod(sim.default_propagation)
    mutate = staticmethod(sim.default_mutation)
    zealot_state = 1
    reset = False
    abc = False

    def __init__(self, cmd_args):
        # Command line arguments
        self.cmd_args = cmd_args
        self.reset = cmd_args.reset
        self.abc = cmd_args.abc

        # Propagation mechanisms
        if cmd_args.propagation == 'majority':
            self.propagate = sim.majority_propagation
        elif cmd_args.propagation == 'minority':
            def f(n, g):
                return sim.majority_propagation(n, g, True)
            self.propagate = f

        # Filename suffix
        self.suffix = '_N_{N}_q_{q}_EPS_{EPS}_S_{SAMPLE_SIZE}_T_{THERM_TIME}' \
                      '_R_{ratio}_p_{propagation}_zn_{n_zealots}'.format_map(vars(cmd_args))

        # 3 states version of the model (abc)
        if self.abc:
            self.mutate = sim.mutation_abc
            self.initialize_states = ng.initial_state_abc
            self.zealot_state = 'a'
            self.suffix = ''.join(['_abc', self.suffix])

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
