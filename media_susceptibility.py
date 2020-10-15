# -*- coding: utf-8 -*-
import os
import json
import numpy as np
from configuration.parser import get_arguments
from tools import convert_to_distributions, split_suffix, plot_mean_std, plot_heatmap, plot_std, plot_mean_per, \
    plot_mean_diff

# parameters of simulations not present in the config module
media_influence = np.arange(0.0, 1.0, 0.1)  # range of considered media influence
bins = 25  # how many bins in heat-map histogram


def plot_media_susceptibility(config):
    """
    Loads the data files saved by main.py and plots them.
    :param config: Config class from configuration module
    """
    # create variables for data
    suffix = split_suffix(config.suffix, 'media')
    l_set = len(media_influence)
    bins_hist = np.linspace(0, 1, num=bins + 1)
    results = {}

    if config.abc:
        media_state = 'a'
    else:
        media_state = str(1)

    for system in config.voting_systems.keys():
        results[system] = {'mean_set': np.zeros(l_set),
                           'std_set': np.zeros(l_set),
                           'hist_set': np.zeros((l_set, bins))}

    # load data
    ylim_mean = [np.inf, -np.inf]
    ylim_std = [0, -np.inf]
    for i, influence in enumerate(media_influence):
        influence = str(influence).replace('.', '')
        influence_string = f'_media_{influence}'
        s = suffix.format(valuetoinsert=influence_string)
        loc = f'results/results{s}.json'
        # print(loc)
        with open(loc) as json_file:
            data = json.load(json_file)
        for system in config.voting_systems.keys():
            distribution = convert_to_distributions(data['results'][system])[media_state]
            dist_mean = np.mean(distribution)
            dist_std = np.std(distribution)
            results[system]['mean_set'][i] = dist_mean
            results[system]['std_set'][i] = dist_std
            results[system]['hist_set'][i, :] = np.histogram(distribution, bins=bins_hist, density=True)[0]
            ylim_mean = [min(ylim_mean[0], dist_mean - dist_std), max(ylim_mean[1], dist_mean + dist_std)]
            ylim_std = [0, max(ylim_std[1], dist_std)]

    # plot figures
    for system in config.voting_systems.keys():
        plot_mean_std(x=media_influence, y=results[system]['mean_set'], std=results[system]['std_set'], 
                      quantity='media', election_system=system, suffix=suffix, xlab='media influence',
                      ylab=f'election result of {media_state}', ylim=ylim_mean, save_file=True)
        plot_heatmap(heatmap=results[system]['hist_set'], l_bins=bins, quantity='media',
                     election_system=system, suffix=suffix, xlab='media influence',
                     ylab=f'distribution of {media_state}', save_file=True, colormap='jet')
        plot_std(x=media_influence, std=results[system]['std_set'], quantity='media', election_system=system,
                 suffix=suffix, xlab='media influence', ylab=f'std of election result of {config.zealot_state}',
                 ylim=ylim_std, save_file=True)
        plot_mean_per(x=media_influence, y=results[system]['mean_set'], quantity='media', election_system=system,
                      suffix=suffix, xlab='media influence', ylab=f'susceptibility per', ylim=(), save_file=True)
        plot_mean_diff(x=media_influence, y=results[system]['mean_set'], quantity='media', election_system=system,
                       suffix=suffix, xlab='media influence', ylab=f'susceptibility derivative', ylim=(),
                       save_file=True)

    #TODO: does this problem still happens sometimes? do we need this?
    #if str(media_state) in convert_to_distributions(data['results']['population']):
    #    population_1 = convert_to_distributions(data['results']['population'])[str(media_state)]
    #else:
    #    population_1 = 0.0
    

if __name__ == '__main__':
    cfg = get_arguments()

    ##################################################################################
    # this section can be modified depending on the environment where you want to run
    # this simulations, e.g. you might want to use multiprocessing to spawn jobs
    # on multiple cores, or just modify the command to use external parallelization,
    # remember if you want to overwrite default parameters for main.py you have to
    # run this script with them and pass them into the main.py run below
    for media in media_influence:
        os.system(f'python3 main.py -mm {media}')
    ##################################################################################

    plot_media_susceptibility(cfg)
