# -*- coding: utf-8 -*-
"""
A collection of helpful functions used in various places of the project
"""
from collections import Counter
from collections.abc import Iterable
import numbers
import os
import json
import time
import numpy as np
from decimal import Decimal

from configuration.logging import log


###########################################################
#                                                         #
#             Reading and writing results                 #
#                                                         #
###########################################################

def prepare_json(_object):
    """
    A function dealing with Counter and Decimal objects
    before dumping the results into a json file.
    The json.JSONEncoder class could be subclassed and
    passed to json.dump 'cls' argument in the future.
    :param _object: the results object to prepare
    :return: the results object ready to dump
    """
    if isinstance(_object, dict) or isinstance(_object, Counter):
        res = {}
        for k, v in _object.items():
            if isinstance(k, numbers.Integral):
                res[str(k)] = prepare_json(v)
            else:
                res[k] = prepare_json(v)
        return res
    elif isinstance(_object, Iterable):
        return [prepare_json(i) for i in _object]
    elif isinstance(_object, Decimal):
        return float(_object)
    return _object


def save_data(config, results, suffix, output_dir='results/'):
    os.makedirs(output_dir, exist_ok=True)
    result = {'settings': config._cmd_args,
              'results': prepare_json(results)}
    fname = output_dir + 'results' + suffix + '.json'
    with open(fname, 'w') as out_file:
        json.dump(result, out_file, indent=3)


def read_data(suffix, input_dir='results/'):
    f_name = input_dir + 'results' + suffix + '.json'
    with open(f_name, 'r') as in_file:
        result = json.load(in_file)
    return result['results'], result['settings']


###########################################################
#                                                         #
#               Computing the results                     #
#                                                         #
###########################################################

def convert_to_distributions(series, missing_value=0):
    """
    Converts a list of dicts into a dict of lists
    :param series: a list of dicts
    :param missing_value: value to insert if a key in a series
    :result: a dict of lists
    """
    # Compute all keys that occur in the series
    keys = set()
    for d in series:
        keys.update(d.keys())
    res = {k: [d[k] if k in d else missing_value for d in series] for k in keys}
    return res


def calculate_indexes(voting_distribution, distribution, sample_size):
    keys = sorted(distribution.keys())
    diff = {}
    value = {}
    for key in keys:
        votes = voting_distribution[key]
        seats = distribution[key]
        diff[key] = np.array(seats) - np.array(votes)
        value[key] = np.array(seats)
    gallagher_index = np.zeros(sample_size)
    loosemore_hanby_index = np.zeros(sample_size)
    effective_number_of_parties = np.zeros(sample_size)
    for i in range(sample_size):
        diffs = np.zeros(len(keys))
        values = np.zeros(len(keys))
        for j, key in enumerate(keys):
            diffs[j] = diff[key][i]
            values[j] = value[key][i]
        gallagher_index[i] = np.sqrt(np.sum(diffs**2)*0.5)
        loosemore_hanby_index[i] = np.sum(np.abs(diffs)) * 0.5
        effective_number_of_parties[i] = 1./np.sum(values**2.)

    return {'Gallagher index': gallagher_index, 'Loosemore Hanby index': loosemore_hanby_index,
            'Eff. No of Parties': effective_number_of_parties}


###########################################################
#                                                         #
#               Other helpful functions                   #
#                                                         #
###########################################################

def run_with_time(func):
    """
    A decorator for counting the execution time
    of a function and printing it once it's finished.
    :param func: a function to decorate
    :return: a decorated function
    """
    def inner(*args, **kwargs):
        start_time = time.time()
        res = func(*args, **kwargs)
        end_time = time.time()

        minutes = (end_time - start_time) / 60.0
        if minutes <= 60:
            log.info(f'Function <{func.__name__}> finished in {round(minutes, 0)} min')
        else:
            log.info(f'Function <{func.__name__}> finished in {round(minutes / 60, 1)} h')

        return res
    return inner


def split_suffix(suffix, parameter):
    parameters_and_values = suffix.split('_')
    parameter_index = parameters_and_values.index(parameter)
    pre_suffix = '_'.join(parameters_and_values[:parameter_index])
    su_suffix = '_'.join(parameters_and_values[(parameter_index+2):])
    if len(su_suffix):
        su_suffix = '_' + su_suffix
    suffix = pre_suffix + '{valuetoinsert}' + su_suffix
    return suffix
