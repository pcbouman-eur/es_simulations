# -*- coding: utf-8 -*-
"""
This file contains configuration for a command line parser based on Python's
argparse module
"""
import argparse
import json

from configuration.config import Config
from electoral_sys.seat_assignment import seat_assignment_rules

# In the following part, the different command line arguments are defined
description = 'Simulation of voting process dynamics with different electoral rules'

parser = argparse.ArgumentParser(description=description)

# Network characteristics
parser.add_argument('-n', type=int, action='store', default=1875, dest='n',
                    help='size of the network')

parser.add_argument('-avg_deg', '--average_degree', action='store', default=5.0, type=float, dest='avg_deg',
                    help='The average degree - defines network density.')

parser.add_argument('-ra', '--ratio', action='store', default=0.1, type=float, dest='ratio',
                    help='The ratio used to plant the affinities')

parser.add_argument('-q', type=int, action='store', default=25, dest='q',
                    help='number of districts')

parser.add_argument('-qn', '--district_sizes', action='store', nargs='+', type=int, default=None, dest='district_sizes',
                    help='The number of voters in districts. Order matters. If this argument is provided, it must be '
                         'of length q, i.e. specified for every district, and size of the network n will be ignored. '
                         'The network will be generated based on the sizes of districts.')

parser.add_argument('-qc', '--district_coords', action='store', type=json.loads, default=None,
                    dest='district_coords',
                    help='The coordinates of the districts. Order matters. If this argument is provided, it must be '
                         'of length q, i.e. specified for every district. If it is not provided a SBM network will '
                         'be generated. The coordinates should be provided as a string, e.g. '
                         '-qc "[[0.0, 1.0], [1.0, 0.0]]"')

parser.add_argument('-gp', '--p_norm', action='store', default=2.0, type=float, dest='p_norm',
                    help='The p-norm used for the distance metric in the planar version of the network.')

parser.add_argument('-gc', '--planar_c', action='store', default=100.0, type=float, dest='planar_c',
                    help='Constant in the function describing link probability for planar graph generator. It may be '
                         'interpreted as the inverse of the link probability inside districts (before normalisation).')


# Electoral system configuration
parser.add_argument('-qs', '--seats', action='store', nargs='+', type=int, default=[1], dest='seats',
                    help='The number of seats per districts. Order matters.'
                         'If there are fewer seats than districts, the list is repeated')

parser.add_argument('-qr', '--seat_rule', action='store', choices=seat_assignment_rules.keys(), dest='seat_rule',
                    default='default',
                    help='The rule used to assign seats within a district. Must be a key from seat_assignment_rules')

parser.add_argument('-tr', '--threshold', action='store', default=0.0, type=float, dest='threshold',
                    help='The electoral threshold (minimal share of votes to be considered)')


# Simulation details
parser.add_argument('-s', '--samples', type=int, action='store', default=500,
                    help='number of points', dest='sample_size')

parser.add_argument('-t', '--therm', type=int, action='store', default=300000,
                    help='thermalization time steps', dest='therm_time')

parser.add_argument('-mc', '--mc_steps', type=int, action='store', default=50, dest='mc_steps',
                    help='number of MC steps between performing consecutive elections in the model')

parser.add_argument('--reset', action='store_const', default=False, const=True, dest='reset',
                    help='whether to reset states after each simulation, draw new zealots and run thermalization again')

parser.add_argument('--random_districts', action='store_const', default=False, const=True, dest='random_dist',
                    help='whether districts should be random and not correspond to the topological communities')

parser.add_argument('--consensus', action='store_const', default=False, const=True, dest='consensus',
                    help='whether to initialize the network in a consensus state (other than the zealot state)')


# Zealots and media configuration
parser.add_argument('-zn', '--zealots_count', type=int, action='store', default=0,
                    help='number of zealots', dest='n_zealots')

parser.add_argument('-zw', '--zealots_where', action='store', default='random',
                    choices=('degree', 'district', 'random'),
                    help='where are the zealots', dest='where_zealots')

parser.add_argument('-zd', '--zealots_district', action='store', default=None, type=int, dest='zealots_district',
                    help='if zealots are in one district, which district')

parser.add_argument('-mm', '--mass_media', type=float, action='store', default=0.5, dest='mass_media',
                    help='independent flip probability to the zealot state - mass media effect')


# Voting process dynamics
parser.add_argument('-e', '--epsilon', type=float, action='store', default=0.01, dest='epsilon',
                    help='noise rate, i.e. the probability of choosing a random state')

parser.add_argument('-p', '--propagation', action='store', default='standard',
                    choices=('standard', 'majority', 'minority'), dest='propagation',
                    help='propagation method to determine a new state based on the states of the neighbours')

# WARNING! When there is more than 2 states/parties the default value of mass media (0.5) is no longer neutral!
parser.add_argument('-np', '--num_parties', type=int, action='store', default=2, dest='num_parties',
                    help='The number of parties to consider, i.e. the number of possible states of nodes')


# File configuration for electoral systems
parser.add_argument('--config_file', action='store', default=None, dest='config_file', type=argparse.FileType('r'),
                    help='The path to a configuration file. It must be in json format and any parameter can '
                         'be provided in the file. Parameters specified in the file take priority over those '
                         'from the command line. The name of the parameter in the file should be the same '
                         'as the name in the namespace ("dest" argument).')


def get_arguments():
    """
    Reads the arguments from the standard in and raises an error if some
    data is missing.
    :result: a Config class object with values for the arguments and other configuration
    """
    # necessary to pass this protected dict in order to trouble-check the redundant parameters
    return Config(parser.parse_args(), parser._option_string_actions)
