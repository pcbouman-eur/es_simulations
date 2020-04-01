# -*- coding: utf-8 -*-
import os
import json
import numpy as np
import itertools
import matplotlib.pyplot as plt
from configuration.parser import get_arguments
from tools import convert_to_distributions

# parameters of simulations
zn_set = range(61)  # range of considered number of zealots
SAMPLE_SIZE = 1000
bins = 25  # how many bins in heatmap histogram


def plot_mean_std(y, std, name, suffix, ylab='election result of 1', x=zn_set, xlab='number of zealots', ylim=(),
                  save_file=True):
    """
    Plots a plot of mean +/- std of given variable vs number of zealots 
    :param y: given variable
    :param std: standard deviation of y
    :param name: name of quantity (Population or District)
    :param suffix: suffix with params values
    :param ylab: y-axis label
    :param x: array with number of zealots
    :param xlab: x-axis label
    :param ylim: y-axis limits as [ymin, ymax]
    :param save_file: bool if save plot to file
    """
    plt.figure(figsize=(4, 3))

    plt.plot(x, y, color='cornflowerblue', linestyle='-')
    plt.plot(x, y + std, color='tomato', linestyle='--')
    plt.plot(x, y - std, color='tomato', linestyle='--')
    if ylim:
        plt.ylim(ylim)

    plt.title(name)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.tight_layout()
    if save_file:
        plt.savefig('plots/zealot_susceptibility_{}{}.pdf'.format(name, suffix))
    else:
        plt.show()


def plot_heatmap(heatmap, l_bins, name, suffix, ylab='distribution of 1', xlab='number of zealots', save_file=True, colormap='jet'):
    """
    Plots a heatmap of given variable vs number of zealots 
    :param heatmap: histogram of given variable
    :param l_bins: number of bins in the distribution
    :param name: name of quantity (Population / District)
    :param suffix: suffix with params values
    :param ylab: y-axis label
    :param xlab: x-axis label
    :param save_file: bool if save plot to file
    :param colormap: change colormap
    """
    transposed_heatmap = np.transpose(heatmap)

    plt.figure(figsize=(3.5, 3.1))
    plt.imshow(transposed_heatmap, origin='lower', aspect='auto', cmap=colormap)
    cb = plt.colorbar()
    cb.ax.tick_params(labelsize=9)

    plt.title(name)
    plt.yticks(np.linspace(0, l_bins, 5) - 0.5, np.linspace(0, 1, 5))
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.tight_layout()
    if save_file:
        plt.savefig('plots/heatmap_zealot_sus_{}{}.pdf'.format(name, suffix))
    else:
        plt.show()


def plot_zealot_susceptibility(config):
    """
    Loads the data files saved by main.py and plots them.
    :param config: Config class from configuration module
    :return: None
    """
    # create variables for data
    suffix = '_N_{N}_q_{q}_EPS_{EPS}_S_{SAMPLE_SIZE}_T_{THERM_TIME}_MC_{mc_steps}_R_{ratio}_p_{propagation}'.format_map(
        vars(config.cmd_args))

    l_zn_set = len(zn_set)

    bins_hist_pop = np.linspace(0, 1, num=bins + 1)
    pop_mean_set = np.zeros(l_zn_set)
    pop_std_set = np.zeros(l_zn_set)
    pop_hist_set = np.zeros((l_zn_set, bins))

    bins_hist_dist = np.linspace(0, 1, num=bins + 1)
    dist_mean_set = np.zeros(l_zn_set)
    dist_std_set = np.zeros(l_zn_set)
    dist_hist_set = np.zeros((l_zn_set, bins))

    # load data
    for i, zn in enumerate(zn_set):
        loc = 'results/results{}_zn_{}.json'.format(suffix, zn)
        with open(loc) as json_file:
            data = json.load(json_file)

        population_1 = convert_to_distributions(data['results']['population'])['1']
        district_1 = convert_to_distributions(data['results']['district'])['1']

        pop_mean_set[i] = np.mean(population_1)
        pop_std_set[i] = np.std(population_1)
        pop_hist_set[i, :] = np.histogram(population_1, bins=bins_hist_pop, normed=True)[0]

        dist_mean_set[i] = np.mean(district_1)
        dist_std_set[i] = np.std(district_1)
        dist_hist_set[i, :] = np.histogram(district_1, bins=bins_hist_dist, normed=True)[0]

    # plot figures
    all_values = list(itertools.chain(dist_mean_set - dist_std_set,
                                      dist_mean_set + dist_std_set,
                                      pop_mean_set - pop_std_set,
                                      pop_mean_set + pop_std_set))
    ylim = [min(all_values), max(all_values)]
    plot_mean_std(pop_mean_set, pop_std_set, 'Multi-member', suffix, ylim=ylim)
    plot_mean_std(dist_mean_set, dist_std_set, 'Single-member', suffix, ylim=ylim)

    plot_heatmap(pop_hist_set, bins, 'Multi-member', suffix)
    plot_heatmap(dist_hist_set, bins, 'Single-member', suffix)


if __name__ == '__main__':
    ##################################################################################
    # this section can be modified depending on the environment where you want to run
    # this simulations, e.g. you might want to use multiprocessing to spawn jobs
    # on multiple cores, or just modify the command to use external parallelization,
    # remember if you want to overwrite default parameters for main.py they should
    # be written at the top of this file to use the same ones for plotting
    for zealots in zn_set:
        os.system('python3 main.py -zn {} -s {}'.format(zealots, SAMPLE_SIZE))
    ##################################################################################

    cfg = get_arguments()
    # here overwrite default configuration parameters with the same values as above
    cfg.cmd_args.SAMPLE_SIZE = SAMPLE_SIZE
    plot_zealot_susceptibility(cfg)
