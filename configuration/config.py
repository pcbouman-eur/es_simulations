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
    :initial_states: a function that generates a vector of initial states
    :propagation: a function that propagates states from neighbours to a node
    :mutation: a function that changes the state of a node at random
    :zealots_config: configuration for the zealot initialization
    :suffix: suggested file name suffix for output files
    """

    def __init__(self, cmd_args):
        # Command line arguments
        self.cmd_args = cmd_args

        # State initialization options
        self.initial_states = ng.default_initial_state

        # Voting systems used in the simulation
        self.voting_systems = {'population' : es.system_population_majority,
                               'district' : es.system_district_majority}

        # Mutation mechanisms
        self.mutation = sim.default_mutation

        # Propagation mechanisms
        if cmd_args.propagation == 'majority':
            self.propagation = sim.majority_propagation
        elif cmd_args.propagation == 'minority':
            self.propagation = lambda n,g: sim.majority_propagation(n,g,True)
        else:
            self.propagation = sim.default_propagation

        # Filename suffix
        self.suffix = '_N_{N}_q_{q}_EPS_{EPS}_S_{SAMPLE_SIZE}_T_{THERM_TIME}'\
                      '_R_{ratio}_p_{propagation}'.format_map(vars(cmd_args))

        # Zealot configuration options
        if cmd_args.where_zealots == 'degree':
            self.zealots_config = {'degree_driven' : True,
                                   'one_district'  : False,
                                   'district'      : None}
        elif cmd_args.where_zealots == 'district':
            self.zealots_config = {'degree_driven' : False,
                                   'one_district'  : True,
                                   'district'      : cmd_args.zealots_district}
        else:
            self.zealots_config = {'degree_driven' : False,
                                   'one_district'  : False,
                                   'district'      : None}                                   


    def initialize_states(self, n):
        """
        Generates an initial state vector for the simulation
        :param n: the number of states to generate
        """
        return self.initial_states(n)

    def propagate(self, target, g):
        """
        Determines a new state for a target node based on the network situation
        :target: the node for which the new state must be determined
        :g: the network where the node lives
        """
        return self.propagation(target, g)
    
    def mutate(self, node):
        """
        Determines a new state for a target node that spontaneously mutates
        its state
        :node: the node that mutates
        """
        return self.mutation(node)