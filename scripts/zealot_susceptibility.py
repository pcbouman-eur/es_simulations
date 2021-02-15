# -*- coding: utf-8 -*-
"""
A script running main.py many times with a given configuration
and changing number of zealots, to then compute and plot
zealot susceptibility and related quantities.
"""
import os
import sys
import json
import numpy as np

sys.path.insert(0, '..')
from configuration.parser import get_arguments
from tools import convert_to_distributions, split_suffix, plot_mean_std, plot_heatmap, plot_std, plot_mean_per, \
    plot_mean_diff

# parameters of simulations not present in the config module
zn_set = range(31)  # range of considered number of zealots


def plot_zealot_susceptibility(config):
    """
    Loads the data files saved by main.py and plots them.
    :param config: Config class from configuration module
    :return: None
    """
    # create variables for data
    suffix = split_suffix(config.suffix, 'zn')
    l_set = len(zn_set)
    bins = config.q + 2
    bins_hist = np.linspace(0, 1, num=bins + 1)
    results = {}
    
    for system in config.voting_systems.keys():
        results[system] = {'mean_set': np.zeros(l_set),
                           'std_set': np.zeros(l_set),
                           'hist_set': np.zeros((l_set, bins))}
    
    # load data
    ylim_mean = [np.inf, -np.inf]
    ylim_std = [0, -np.inf]
    for i, zn in enumerate(zn_set):
        zn_string = f'_zn_{zn}'
        s = suffix.format(valuetoinsert=zn_string)
        loc = f'results/results{s}.json'
        with open(loc) as json_file:
            data = json.load(json_file)
        for system in config.voting_systems.keys():
            distribution = convert_to_distributions(data['results'][system])[str(config.zealot_state)]
            dist_mean = np.mean(distribution)
            dist_std = np.std(distribution)
            results[system]['mean_set'][i] = dist_mean
            results[system]['std_set'][i] = dist_std
            results[system]['hist_set'][i, :] = np.histogram(distribution, bins=bins_hist, density=True)[0]
            ylim_mean = [min(ylim_mean[0], dist_mean - dist_std), max(ylim_mean[1], dist_mean + dist_std)]
            ylim_std = [0, max(ylim_std[1], dist_std)]

    # plot figures
    for system in config.voting_systems.keys():
        plot_mean_std(x=zn_set, y=results[system]['mean_set'], std=results[system]['std_set'], 
                      quantity='zealots', election_system=system, suffix=suffix, xlab='number of zealots',
                      ylab=f'election result of {config.zealot_state}', ylim=ylim_mean, save_file=True)
        plot_heatmap(heatmap=results[system]['hist_set'], l_bins=bins, quantity='zealots', 
                     election_system=system, suffix=suffix, xlab='number of zealots', 
                     ylab=f'distribution of {config.zealot_state}', save_file=True, colormap='jet')
        plot_std(x=zn_set, std=results[system]['std_set'], quantity='zealots', election_system=system, suffix=suffix,
                 xlab='number of zealots', ylab=f'std of election result of {config.zealot_state}', ylim=ylim_std,
                 save_file=True)
        plot_mean_per(x=zn_set, y=results[system]['mean_set'], quantity='zealots', election_system=system,
                      suffix=suffix, xlab='number of zealots', ylab=f'susceptibility per', ylim=(), save_file=True)
        plot_mean_diff(x=zn_set, y=results[system]['mean_set'], quantity='zealots', election_system=system,
                       suffix=suffix, xlab='number of zealots', ylab=f'susceptibility derivative',
                       ylim=(), save_file=True)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.getcwd()))
    cfg = get_arguments()

    ##################################################################################
    # this section can be modified depending on the environment where you want to run
    # this simulations, e.g. you might want to use multiprocessing to spawn jobs
    # on multiple cores, or just modify the command to use external parallelization,
    # remember if you want to overwrite default parameters for main.py you have to
    # run this script with them and pass them into the main.py run below, a convenient
    # way of doing it is by creating a configuration file and passing just the file
    # for this script and here below, careful not to set -zn param in the file
    for zealots in zn_set:
        os.system(f'python3 main.py -zn {zealots} --config_file {cfg.config_file}')
    ##################################################################################
    plot_zealot_susceptibility(cfg)
