"""
This file contains configuration for a command line parser based on Python's
argparse module
"""

import argparse
from configuration.config import Config

# In the following part, the different command line arguments are defined

description = 'Simulation of dynamics in the voter model'

parser = argparse.ArgumentParser(description=description)

parser.add_argument('-N', type=int, action='store', default=1875, dest='N',
                    help='size of the network')

parser.add_argument('-q', type=int, action='store', default=25, dest='q',
                    help='number of districts')

parser.add_argument('-e', '--EPS', type=float, action='store', default=0.01,
                    dest='EPS', help='noise rate')

parser.add_argument('-s', '--samples', type=int, action='store', default=500,
                    help='number of points', dest='SAMPLE_SIZE')

parser.add_argument('-t', '--therm', type=int, action='store', default=300000,
                    help='thermalization time steps', dest='THERM_TIME')

parser.add_argument('-mc', '--mc_steps', type=int, action='store', default=50,
                    help='number of MC steps between performing consecutive elections in the model',
                    dest='mc_steps')

parser.add_argument('-zn', '--zealots_count', type=int, action='store',
                    default=0, help='number of zealots', dest='n_zealots')

parser.add_argument('-zw', '--zealots_where', action='store', default='random',
                    choices=('degree', 'district', 'random'),
                    help='where are the zealots', dest='where_zealots')

parser.add_argument('-zd', '--zealots_district', action='store', default=None,
                    type=int, dest='zealots_district',
                    help='if zealots are in one district, which district')

parser.add_argument('-ra', '--ratio', action='store', default=0.1,
                    type=float, dest='ratio',
                    help='The ratio used to plant the affinities')

parser.add_argument('--reset', action='store_const', default=False, const=True, dest='reset',
                    help='whether to reset states after each simulation, draw new zealots and run thermalization again')

parser.add_argument('-p', '--propagation', action='store', default='standard',
                    choices=('standard', 'majority', 'minority'),
                    dest='propagation',
                    help='propagation method to determine a new state based on '
                         'the states of the neighbours')

parser.add_argument('--abc', action='store_const', default=False, const=True,
                    dest='abc', help='if you want to run simulation for 3 states a, b, and c')


def get_arguments():
    """
    Reads the arguments from the standard out and raises an error if some
    data is missing.

    :result: a Namespace object with values for the arguments
    """
    return Config(parser.parse_args())

