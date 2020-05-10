# -*- coding: utf-8 -*-
import os
import json
import numpy as np
import itertools
import matplotlib.pyplot as plt
from configuration.parser import get_arguments
from tools import convert_to_distributions

# parameters of simulations not present in the config module
media_influence = np.arange(0.0, 1.0, 0.04)  # range of considered media influence
bins = 25  # how many bins in heat-map histogram


def plot_mean_std(y, std, name, suffix, y_lab='election result of 1', x=media_influence,
                  x_lab='media influence', y_lim=(), save_file=True):
    """
    Plots a plot of mean +/- std of given variable vs mass media influence
    :param y: given variable
    :param std: standard deviation of y
    :param name: name of quantity (Population or District)
    :param suffix: suffix with params values
    :param y_lab: y-axis label
    :param x: array with distinct media influence
    :param x_lab: x-axis label
    :param y_lim: y-axis limits as [ymin, ymax]
    :param save_file: bool if save plot to file
    """
    plt.figure(figsize=(4, 3))

    plt.plot(x, y, color='cornflowerblue', linestyle='-')
    plt.plot(x, y + std, color='tomato', linestyle='--')
    plt.plot(x, y - std, color='tomato', linestyle='--')
    if y_lim:
        plt.ylim(y_lim)

    plt.title(name)
    plt.xlabel(x_lab)
    plt.ylabel(y_lab)
    plt.tight_layout()
    if save_file:
        plt.savefig('plots/media_susceptibility_{}{}{}.pdf'.format(name, suffix[0], suffix[2]))
    else:
        plt.show()


def plot_heat_map(heat_map, l_bins, name, suffix, y_lab='distribution of 1', x_lab='media influence',
                  save_file=True, colormap='jet'):
    """
    Plots a heat map of given variable vs mass media influence
    :param heat_map: histogram of given variable
    :param l_bins: number of bins in the distribution
    :param name: name of quantity (Population / District)
    :param suffix: suffix with params values
    :param y_lab: y-axis label
    :param x_lab: x-axis label
    :param save_file: bool if save plot to file
    :param colormap: change colormap
    """
    transposed_heat_map = np.transpose(heat_map)

    plt.figure(figsize=(3.5, 3.1))
    plt.imshow(transposed_heat_map, origin='lower', aspect='auto', cmap=colormap)
    cb = plt.colorbar()
    cb.ax.tick_params(labelsize=9)

    plt.title(name)
    plt.yticks(np.linspace(0, l_bins, 5) - 0.5, np.linspace(0, 1, 5))
    plt.xlabel(x_lab)
    plt.ylabel(y_lab)
    plt.tight_layout()
    if save_file:
        plt.savefig('plots/heat_map_media_sus_{}{}{}.pdf'.format(name, suffix[0], suffix[2]))
    else:
        plt.show()


def split_suffix(suffix, parameter):
    parameters_and_values = suffix.split('_')
    parameter_index = parameters_and_values.index(parameter)
    pre_suffix = '_'.join(parameters_and_values[:parameter_index])
    param_suffix = '_' + parameters_and_values[parameter_index] + '_'
    su_suffix = '_' + '_'.join(parameters_and_values[(parameter_index+2):])
    return pre_suffix, param_suffix, su_suffix


def plot_media_susceptibility(config):
    """
    Loads the data files saved by main.py and plots them.
    :param config: Config class from configuration module
    """
    # create variables for data
    suffix = split_suffix(config.suffix, 'media')
    media_influence_n = len(media_influence)

    bins_hist_pop = np.linspace(0, 1, num=bins+1)
    pop_mean_set = np.zeros(media_influence_n)
    pop_std_set = np.zeros(media_influence_n)
    pop_hist_set = np.zeros((media_influence_n, bins))

    bins_hist_dist = np.linspace(0, 1, num=bins+1)
    dist_mean_set = np.zeros(media_influence_n)
    dist_std_set = np.zeros(media_influence_n)
    dist_hist_set = np.zeros((media_influence_n, bins))

    if config.abc:
        media_state = 'a'
    else:
        media_state = 1

    # load data
    for i, influence in enumerate(media_influence):
        loc = 'results/results{}{}{}{}.json'.format(suffix[0], suffix[1], influence, suffix[2])
        with open(loc) as json_file:
            data = json.load(json_file)

        population_1 = convert_to_distributions(data['results']['population'])[str(media_state)]
        district_1 = convert_to_distributions(data['results']['district'])[str(media_state)]

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
    y_lim = [min(all_values), max(all_values)]

    plot_mean_std(pop_mean_set, pop_std_set, 'Multi-member', suffix, y_lim=y_lim,
                  y_lab='election result of {}'.format(media_state))
    plot_mean_std(dist_mean_set, dist_std_set, 'Single-member', suffix, y_lim=y_lim,
                  y_lab='election result of {}'.format(media_state))

    plot_heat_map(pop_hist_set, bins, 'Multi-member', suffix,
                  y_lab='distribution of {}'.format(media_state))
    plot_heat_map(dist_hist_set, bins, 'Single-member', suffix,
                  y_lab='distribution of {}'.format(media_state))


if __name__ == '__main__':
    cfg = get_arguments()

    ##################################################################################
    # this section can be modified depending on the environment where you want to run
    # this simulations, e.g. you might want to use multiprocessing to spawn jobs
    # on multiple cores, or just modify the command to use external parallelization,
    # remember if you want to overwrite default parameters for main.py you have to
    # run this script with them and pass them into the main.py run below
    for media in media_influence:
        os.system('python3 main.py -mm {} -s {}'.format(media, cfg.cmd_args.SAMPLE_SIZE))
    ##################################################################################

    plot_media_susceptibility(cfg)
