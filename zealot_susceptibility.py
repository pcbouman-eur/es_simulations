# -*- coding: utf-8 -*-
import os
import json
import numpy as np
import itertools
import matplotlib.pyplot as plt
from configuration.parser import get_arguments
from tools import convert_to_distributions, split_suffix, plot_mean_std, plot_heatmap

# parameters of simulations not present in the config module
zn_set = range(6)  # range of considered number of zealots
bins = 25  # how many bins in heatmap histogram

def plot_zealot_susceptibility(config):
    """
    Loads the data files saved by main.py and plots them.
    :param config: Config class from configuration module
    :return: None
    """
    # create variables for data
    #suffix = split_suffix(config.suffix, 'zn')
    suffix = config.suffix.split('_zn_')[0]
    l_zn_set = len(zn_set)
    bins_hist = np.linspace(0, 1, num=bins + 1)
    results = {}
    
    for system in cfg.voting_systems.keys():
        results[system] = {'mean_set':np.zeros(l_zn_set), 
                           'std_set':np.zeros(l_zn_set), 
                           'hist_set':np.zeros((l_zn_set, bins))}
    
    # load data
    ylim = [np.inf, -np.inf]
    for i, zn in enumerate(zn_set):
        loc = 'results/results{}_zn_{}.json'.format(suffix, zn)
        with open(loc) as json_file:
            data = json.load(json_file)
        for system in cfg.voting_systems.keys():
            distribution = convert_to_distributions(data['results'][system])[str(config.zealot_state)]
            dist_mean = np.mean(distribution)
            dist_std = np.std(distribution)
            results[system]['mean_set'][i] = dist_mean
            results[system]['std_set'][i] = dist_std
            results[system]['hist_set'][i,:] = np.histogram(distribution, bins=bins_hist, density=True)[0]
            ylim = [min(ylim[0], dist_mean - dist_std), max(ylim[1], dist_mean + dist_std)]

    # plot figures
    for system in cfg.voting_systems.keys():
        plot_mean_std(x=zn_set, y=results[system]['mean_set'], std=results[system]['std_set'], 
                      quantity='zealots', election_system=system, suffix=suffix, xlab='number of zealots',
                      ylab=f'election result of {config.zealot_state}', ylim=ylim, save_file=True)
        plot_heatmap(heatmap=results[system]['hist_set'], l_bins=bins, quantity='zealots', 
                     election_system=system, suffix=suffix, xlab='number of zealots', 
                     ylab=f'distribution of {config.zealot_state}', save_file=True, colormap='jet')

if __name__ == '__main__':
    cfg = get_arguments()

    ##################################################################################
    # this section can be modified depending on the environment where you want to run
    # this simulations, e.g. you might want to use multiprocessing to spawn jobs
    # on multiple cores, or just modify the command to use external parallelization,
    # remember if you want to overwrite default parameters for main.py you have to
    # run this script with them and pass them into the main.py run below
    #for zealots in zn_set:
    #    print(cfg.suffix)
    #    os.system(f'/Users/jklamut/anaconda3/bin/python3 main.py --abc -zn {zealots} -s {cfg.cmd_args.SAMPLE_SIZE} -t {cfg.cmd_args.THERM_TIME}')
    ##################################################################################
    plot_zealot_susceptibility(cfg)
