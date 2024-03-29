# -*- coding: utf-8 -*-
"""
A script running main.py many times with a given configuration
and changing number of zealots and mass media influence,
to then compute and plot comparision between them.
"""
import numpy as np
import json
import os
import sys
import inspect
from matplotlib import pyplot as plt

# path hack for imports to work when running this script from any location,
# without the hack one has to manually edit PYTHONPATH every time
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from configuration.parser import get_arguments
from tools import convert_to_distributions

# parameters of simulations not present in the config module
zn_set = np.arange(61)  # range of considered number of zealots
media_influence = np.arange(0.0, 1.0, 0.02)  # range of considered media influence


def create_heatmap(data, system, suffix, name='mean', save=True):
    """
    Draws a heatmap based on data variable.

    :param data: two dimensional matrix of values for the heatmap (numpy.array)
    :param system: name of electoral system (string)
    :param suffix: suffix with params values (string)
    :param name: name of the variable - mean, std etc. (string)
    :param save: variable deciding whether to save the plot or not (bool)
    """
    plt.figure(figsize=(3.5, 3.1))
    plt.imshow(data.T, origin='lower', aspect='auto', cmap='jet')
    cb = plt.colorbar()
    cb.ax.tick_params(labelsize=9)

    plt.title(system + ' - ' + name)
    plt.xlabel('media')
    plt.ylabel('zealots')
    plt.xticks(np.linspace(0, media_influence.shape[0], 5) - 0.5, np.linspace(0, 1, 5))
    plt.tight_layout()
    if save:
        plt.savefig(f'plots/media_vs_zealots_{system}{suffix}_{name}.png')
    else:
        plt.show()


def plot_media_vs_zealots(config):
    """
    Loads the data files saved by main.py and plots them.

    :param config: Config class from configuration module (Config)
    """
    # create suffix with both media and zealots
    parameters_and_values = config.suffix.split('_')
    media_index = parameters_and_values.index('media')
    zealots_index = parameters_and_values.index('zn')
    first_index = min(media_index, zealots_index)
    second_index = max(media_index, zealots_index)
    pre_suffix = '_'.join(parameters_and_values[:first_index])
    inter_suffix = '_'.join(parameters_and_values[(first_index+2):second_index])
    if len(inter_suffix):
        inter_suffix = '_' + inter_suffix
    su_suffix = '_'.join(parameters_and_values[(second_index+2):])
    if len(su_suffix):
        su_suffix = '_' + su_suffix
    if media_index < zealots_index:
        suffix = pre_suffix + '{media_value}' + inter_suffix + '{zn_value}' + su_suffix
    elif media_index > zealots_index:
        suffix = pre_suffix + '{zn_value}' + inter_suffix + '{media_value}' + su_suffix
    else:
        raise Exception("There is an issue with media or zealots index in the suffix.")

    shown_state = config.zealot_state

    results = {}
    for system in config.voting_systems.keys():
        results[system] = {'mean': np.zeros((len(media_influence), len(zn_set))),
                           'std': np.zeros((len(media_influence), len(zn_set)))}

    # load data
    for i, influence in enumerate(media_influence):
        for j, zn in enumerate(zn_set):
            influence = str(influence).replace('.', '')
            influence_string = f'_media_{influence}'
            zn_string = f'_zn_{zn}'
            s = suffix.format(zn_value=zn_string, media_value=influence_string)
            loc = f'results/results{s}.json'
            with open(loc) as json_file:
                data = json.load(json_file)
            for system in config.voting_systems.keys():
                distribution = convert_to_distributions(data['results'][system])[shown_state]
                dist_mean = np.mean(distribution)
                dist_std = np.std(distribution)
                results[system]['mean'][i, j] = dist_mean
                results[system]['std'][i, j] = dist_std

    # plot figures
    s = suffix.format(zn_value='', media_value='')
    for system in config.voting_systems.keys():
        create_heatmap(results[system]['mean'], system, s, name='mean', save=True)
        create_heatmap(results[system]['std'], system, s, name='std', save=True)


def run_sim(cfg, media, zealots):
    os.system(f'python3 main.py -mm {media} -zn {zealots} --config_file {cfg.config_file}')


if __name__ == '__main__':
    os.chdir(parentdir)
    cfg = get_arguments()

    ##################################################################################
    # this section can be modified depending on the environment where you want to run
    # this simulations, e.g. you might want to use multiprocessing to spawn jobs
    # on multiple cores, or just modify the command to use external parallelization,
    # remember if you want to overwrite default parameters for main.py you have to
    # run this script with them and pass them into the main.py run below, a convenient
    # way of doing it is by creating a configuration file and passing just the file
    # for this script and here below, careful not to set -mm and -zn params in the file
    for media in media_influence:
        for zealots in zn_set:
            run_sim(cfg, media, zealots)
    ##################################################################################

    plot_media_vs_zealots(cfg)
