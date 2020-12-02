# -*- coding: utf-8 -*-
from collections import Counter
from collections.abc import Iterable
import numbers
import os
import json
import time
import numpy as np
from matplotlib import pyplot as plt

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


def prepare_json(d):
    if isinstance(d, dict) or isinstance(d, Counter):
        res = {}
        for k, v in d.items():
            if isinstance(k, numbers.Integral):
                res[str(k)] = prepare_json(v)
            else:
                res[k] = prepare_json(v)
        return res
    if isinstance(d, Iterable):
        return [prepare_json(i) for i in d]
    return d


def plot_hist(distribution, name, suffix, output_dir='plots/', colors=('tomato', 'mediumseagreen', 'cornflowerblue')):
    os.makedirs(output_dir, exist_ok=True)

    for idx, key in enumerate(sorted(distribution.keys())):
        col = colors[idx % len(colors)]
        distr = distribution[key]

        plt.figure(figsize=(4, 3))
        plt.hist(distr, bins=np.linspace(0.0, 1.0, 21), range=(0, 1), density=True, color=col)

        avg = np.mean(distr)
        std = np.std(distr)
        plt.axvline(avg, linestyle='-', color='black')
        plt.axvline(avg - std, linestyle='--', color='black')
        plt.axvline(avg + std, linestyle='--', color='black')

        plt.title('Histogram of seats share, avg={}, std={}'.format(round(avg, 2), round(std, 2)))
        plt.xlabel('fraction of seats')
        plt.ylabel('probability')

        plt.tight_layout()
        plt.savefig(output_dir + name + '_' + str(key) + suffix + '.pdf')

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


def plot_indexes(indexes, name, suffix, output_dir='plots/'):
    for index, values in indexes.items():
        lim0 = np.min([0, np.min(values)])
        lim1 = np.max([1, np.max(values)])

        plt.figure(figsize=(4, 3))
        plt.hist(values, bins=np.linspace(lim0, lim1, 21), range=(0, 1), density=True)

        avg = np.mean(values)
        std = np.std(values)
        plt.axvline(avg, linestyle='-', color='black')
        plt.axvline(avg - std, linestyle='--', color='black')
        plt.axvline(avg + std, linestyle='--', color='black')

        plt.title(f'Histogram of {index} \n avg={round(avg, 2)}, std={round(std, 2)}')
        plt.xlabel(f'{index}')
        plt.ylabel('probability')

        plt.tight_layout()
        plt.savefig(output_dir + name + '_' + index + suffix + '.pdf')


def plot_traj(traj, suffix, output_dir='plots/', colors=('tomato', 'mediumseagreen', 'cornflowerblue')):
    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(4, 3))

    for i, key in enumerate(sorted(traj.keys())):
        plt.plot(traj[key], color=colors[i % len(colors)], label=str(key))

    plt.ylim(0, 1)
    plt.legend()

    plt.xlabel('time steps [in hundreds]')
    plt.ylabel('fraction of N')
    plt.title('Trajectory during thermalization')

    plt.tight_layout()
    plt.savefig('{}/trajectory{}.pdf'.format(output_dir, suffix))


def save_data(config, results, suffix, output_dir='results/'):
    os.makedirs(output_dir, exist_ok=True)
    result = {'settings': vars(config.cmd_args),
              'results': prepare_json(results)}
    fname = output_dir + 'results' + suffix + '.json'
    with open(fname, 'w') as out_file:
        json.dump(result, out_file, indent=3)


def read_data(suffix, input_dir='results/'):
    f_name = input_dir + 'results' + suffix + '.json'
    with open(f_name, 'r') as in_file:
        result = json.load(in_file)
    return result['results'], result['settings']


def run_with_time(func):
    def inner(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()

        minutes = (end_time - start_time) / 60.0
        if minutes <= 60:
            print(f'Function <{func.__name__}> finished in {round(minutes, 0)} min')
        else:
            print(f'Function <{func.__name__}> finished in {round(minutes / 60, 1)} h')
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


def plot_mean_std(x, y, std, quantity, election_system, suffix, xlab, 
                  ylab='election result of 1', ylim=(), save_file=True):
    """
    Plots mean +/- std of given variable vs quantity (eg number of zealots)
    :param x: array with considered quantitity (zealots / media influence)
    :param y: given variable
    :param std: standard deviation of 
    :param quantity: we calculate susceptibility of that quantity
    :param election_system: name of election system
    :param suffix: suffix with params values
    :param xlab: x-axis label
    :param ylab: y-axis label
    :param ylim: y-axis limits as [ymin, ymax]
    :param save_file: bool if save plot to file
    """
    plt.figure(figsize=(4, 3))

    plt.plot(x, y, color='cornflowerblue', linestyle='-')
    plt.plot(x, y + std, color='tomato', linestyle='--')
    plt.plot(x, y - std, color='tomato', linestyle='--')
    if ylim:
        plt.ylim(ylim)

    plt.title(election_system)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.tight_layout()
    if save_file:
        s = suffix.format(valuetoinsert='')
        plt.savefig(f'plots/{quantity}_susceptibility_{election_system}{s}.pdf')
    else:
        plt.show()


def plot_std(x, std, quantity, election_system, suffix, xlab,
             ylab='election result of 1', ylim=(), save_file=True):
    """
    Plots std of given variable vs quantity (eg number of zealots)
    :param x: array with considered quantitity (zealots / media influence)
    :param std: standard deviation of
    :param quantity: we calculate susceptibility of that quantity
    :param election_system: name of election system
    :param suffix: suffix with params values
    :param xlab: x-axis label
    :param ylab: y-axis label
    :param ylim: y-axis limits as [ymin, ymax]
    :param save_file: bool if save plot to file
    """
    plt.figure(figsize=(4, 3))

    plt.plot(x, std, color='tomato', linestyle='-')
    if ylim:
        plt.ylim(ylim)

    plt.title(election_system)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.tight_layout()
    if save_file:
        s = suffix.format(valuetoinsert='')
        plt.savefig(f'plots/{quantity}_std_{election_system}{s}.pdf')
    else:
        plt.show()


def plot_mean_diff(x, y, quantity, election_system, suffix, xlab,
                   ylab='derivative of susceptibility', ylim=(), save_file=True):
    """
    Plots (right) derivative of mean of given variable vs quantity (eg number of zealots)
    :param x: array with considered quantitity (zealots / media influence)
    :param y: given variable
    :param quantity: we calculate susceptibility of that quantity
    :param election_system: name of election system
    :param suffix: suffix with params values
    :param xlab: x-axis label
    :param ylab: y-axis label
    :param ylim: y-axis limits as [ymin, ymax]
    :param save_file: bool if save plot to file
    """
    plt.figure(figsize=(4, 3))

    plt.plot(x[:-1], (y[1:]-y[:-1])/np.diff(x), color='mediumseagreen', linestyle='-')
    if ylim:
        plt.ylim(ylim)

    plt.title(election_system)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.tight_layout()
    if save_file:
        s = suffix.format(valuetoinsert='')
        plt.savefig(f'plots/{quantity}_derivative_{election_system}{s}.pdf')
    else:
        plt.show()


def plot_mean_per(x, y, quantity, election_system, suffix, xlab,
                  ylab='relative result', ylim=(), save_file=True):
    """
    Plots change of mean of given variable divided by quantity (eg divided by number of zealots)
    :param x: array with considered quantitity (zealots / media influence)
    :param y: given variable
    :param quantity: we calculate susceptibility of that quantity
    :param election_system: name of election system
    :param suffix: suffix with params values
    :param xlab: x-axis label
    :param ylab: y-axis label
    :param ylim: y-axis limits as [ymin, ymax]
    :param save_file: bool if save plot to file
    """
    plt.figure(figsize=(4, 3))

    plt.plot(x[1:], (y[1:]-y[0])/x[1:], color='mediumseagreen', linestyle='-')
    if ylim:
        plt.ylim(ylim)

    plt.title(election_system)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.tight_layout()
    if save_file:
        s = suffix.format(valuetoinsert='')
        plt.savefig(f'plots/{quantity}_susceptibilityPer_{election_system}{s}.pdf')
    else:
        plt.show()


def plot_heatmap(heatmap, l_bins, quantity, election_system, suffix, xlab='number of zealots', 
                 ylab='distribution of 1', save_file=True, colormap='jet'):
    """
    Plots a heatmap of given variable vs given quantity (eg number of zealots)
    :param heatmap: histogram of given variable
    :param l_bins: number of bins in the distribution
    :param quantity: we calculate susceptibility of that quantity
    :param election_system: name of electoral system
    :param suffix: suffix with params values
    :param xlab: x-axis label
    :param ylab: y-axis label
    :param save_file: bool if save plot to file
    :param colormap: change colormap
    """
    transposed_heatmap = np.transpose(heatmap)

    plt.figure(figsize=(3.5, 3.1))
    plt.imshow(transposed_heatmap, origin='lower', aspect='auto', cmap=colormap)
    cb = plt.colorbar()
    cb.ax.tick_params(labelsize=9)

    plt.title(election_system)
    plt.yticks(np.linspace(0, l_bins, 5) - 0.5, np.linspace(0, 1, 5))
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.tight_layout()
    if save_file:
        s = suffix.format(valuetoinsert='')
        plt.savefig(f'plots/heatmap_{quantity}_susceptibility_{election_system}{s}.pdf')
    else:
        plt.show()
