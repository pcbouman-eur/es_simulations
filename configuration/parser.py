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

parser.add_argument('-zn', '--zealots_count', type=int, action='store',
                    default=6, help='number of zealots', dest='n_zealots')

parser.add_argument('-zw', '--zealots_where', action='store', default='random',
                    choices=('degree', 'district', 'random'),
                    help='where are the zealots', dest='where_zealots')

parser.add_argument('-zd', '--zealots_district', action='store', default=None,
                    type=int, dest='zealots_district',
                    help='if zealots are in one district, which district')

parser.add_argument('-r', '--ratio', action='store', default=0.1,
                    type=float, dest='ratio',
                    help='The ratio used to plant the affinities')

parser.add_argument('-p', '--propagation', action='store', default='standard',
                    choices=('standard', 'majority', 'minority'),
                    dest='propagation',
                    help='propagation method to determine a new state based on '
                    'the states of the neighbours')



def get_arguments():
    """
    Reads the arguments from the standard out and raises an error if some
    data is missing.

    :result: a Namespace object with values for the arguments
    """
    return Config(parser.parse_args())


"""
The defaults in this file were based on the following code snippet from run.py

if len(sys.argv) == 1:
    N = 1875
    q = 25
    EPS = 0.01
    SAMPLE_SIZE = 500
    THERM_TIME = 300000
    n_zealots = 6  # round(N/50)
    where_zealots = 'district'
    zealots_district = None
else:
    N = int(sys.argv[1])  # size of the network
    q = int(sys.argv[2])  # number of districts
    EPS = float(sys.argv[3])  # noise rate
    SAMPLE_SIZE = int(sys.argv[4])  # number of points
    THERM_TIME = int(sys.argv[5])  # thermalization time steps
    n_zealots = int(sys.argv[6])  # number of zealots
    where_zealots = chr(sys.argv[7])  # where are the zealots. Options: degree-based, one_district, random
    zealots_district = int(sys.argv[8])  # if zealots are in one district, which district
"""