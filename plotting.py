# -*- coding: utf-8 -*-
"""
A collection of plotting functions used to generate figures
"""
import os
import numpy as np
import igraph as ig
from numpy.random import normal
from matplotlib import pyplot as plt


COLORS = (
    'tomato', 'mediumseagreen', 'cornflowerblue', 'mediumorchid',
    'sandybrown', 'gold', 'deepskyblue', 'orangered', 'goldenrod'
)


###########################################################
#                                                         #
#                  Plotting functions                     #
#                                                         #
###########################################################

def plot_traj(traj, suffix, output_dir='plots/', colors=COLORS):
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
    plt.savefig('{}/trajectory{}.png'.format(output_dir, suffix))
    plt.close('all')


def plot_hist(distribution, name, suffix, bins_num=21, output_dir='plots/', colors=COLORS):
    os.makedirs(output_dir, exist_ok=True)

    for idx, key in enumerate(sorted(distribution.keys())):
        col = colors[idx % len(colors)]
        distr = distribution[key]

        plt.figure(figsize=(4, 3))
        plt.hist(distr, bins=np.linspace(0.0, 1.0, bins_num), range=(0, 1), density=True, color=col)

        avg = np.mean(distr)
        std = np.std(distr)
        plt.axvline(avg, linestyle='-', color='black')
        plt.axvline(avg - std, linestyle='--', color='black')
        plt.axvline(avg + std, linestyle='--', color='black')

        plt.title('Histogram of seats share, avg={}, std={}'.format(round(avg, 2), round(std, 2)))
        plt.xlabel('fraction of seats')
        plt.ylabel('probability')

        plt.tight_layout()
        plt.savefig(output_dir + name + '_' + str(key) + suffix + '.png')
        plt.close('all')


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
        plt.savefig(output_dir + name + '_' + index + suffix + '.png')
        plt.close('all')


def plot_mean_std(x, y, std, quantity, election_system, suffix, xlab,
                  ylab='election result of a', ylim=(), save_file=True):
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
        plt.savefig(f'plots/{quantity}_susceptibility_{election_system}{s}.png')
    else:
        plt.show()
    plt.close('all')


def plot_mean_std_two_systems(x, y1, std1, y1_name, y2, std2, y2_name, quantity, suffix, xlab,
                              ylab='election result of a', ylim=(), save_file=True):
    """
    Plots mean +/- std of 2 variables vs quantity (eg number of zealots)
    :param x: array with considered quantity (zealots / media influence)
    :param y1: variable 1
    :param std1: standard deviation of y1
    :param y1_name: name of y1 in the legend
    :param y2: variable 2
    :param std2: standard deviation of y2
    :param y2_name: name of y2 in the legend
    :param quantity: we calculate susceptibility over that quantity
    :param suffix: suffix with params values
    :param xlab: x-axis label
    :param ylab: y-axis label
    :param ylim: y-axis limits as [ymin, ymax]
    :param save_file: bool if save plot to file
    """
    plt.figure(figsize=(4, 3))

    plt.plot(x, y1, color='cornflowerblue', linestyle='-', label=y1_name)
    plt.plot(x, y2, color='tomato', linestyle='-', label=y2_name)

    plt.fill_between(x, y1 - std1, y1 + std1, color='cornflowerblue', linewidth=0, alpha=0.5)
    plt.fill_between(x, y2 - std2, y2 + std2, color='tomato', linewidth=0, alpha=0.5)

    if ylim:
        plt.ylim(ylim)

    plt.title(f'{quantity} susceptibility')
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.legend()
    plt.tight_layout()
    if save_file:
        s = suffix.format(valuetoinsert='')
        plt.savefig(f'plots/{quantity}_sus_comparison{s}.png')
    else:
        plt.show()
    plt.close('all')


def plot_mean_std_all(voting_systems, x, results, quantity, suffix, xlab, ylab='election result of a', ylim=(),
                      save_file=True):
    """
    Plots mean +/- std of all electoral systems from results vs quantity (eg number of zealots)
    :param voting_systems: iterable with names of electoral systems
    :param x: array with considered quantity (zealots / media influence)
    :param results: dict with results with keys 'mean_set' and 'std_set' (e.g. prepared in zealot_susceptibility.py)
    :param quantity: we calculate susceptibility over that quantity
    :param suffix: suffix with params values
    :param xlab: x-axis label
    :param ylab: y-axis label
    :param ylim: y-axis limits as [ymin, ymax]
    :param save_file: bool if save plot to file
    """
    plt.figure(figsize=(4, 3))

    for i, system in enumerate(voting_systems):
        plt.plot(x, results[system]['mean_set'], color=COLORS[i % len(COLORS)], linestyle='-', label=system)
        plt.fill_between(x, results[system]['mean_set'] - results[system]['std_set'],
                         results[system]['mean_set'] + results[system]['std_set'],
                         color=COLORS[i % len(COLORS)], linewidth=0, alpha=0.5)

    if ylim:
        plt.ylim(ylim)

    plt.title(f'{quantity} susceptibility')
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.legend()
    plt.tight_layout()
    if save_file:
        s = suffix.format(valuetoinsert='')
        plt.savefig(f'plots/{quantity}_sus_all{s}.png')
    else:
        plt.show()
    plt.close('all')


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
        plt.savefig(f'plots/{quantity}_std_{election_system}{s}.png')
    else:
        plt.show()
    plt.close('all')


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
        plt.savefig(f'plots/{quantity}_derivative_{election_system}{s}.png')
    else:
        plt.show()
    plt.close('all')


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
        plt.savefig(f'plots/{quantity}_susceptibilityPer_{election_system}{s}.png')
    else:
        plt.show()
    plt.close('all')


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
        plt.savefig(f'plots/heatmap_{quantity}_susceptibility_{election_system}{s}.png')
    else:
        plt.show()
    plt.close('all')


def plot_network(graph, config, mode=None, layout=None, save_as=None, node_size=10, std=0.00015, ig_layout=None):
    """
    Plotting igraph.Graph() object in various ways, indicating with color districts or states of the dones.
    :param graph: the network to plot, igraph.Graph() object
    :param config: configuration of the simulation, config.Config() object
    :param mode: either 'districts' to plot districts, or 'states' to plot states
    :param layout: 'default', 'geo', or 'geo_strict', the mode of plotting the net, if None it'll be 'default'
    :param save_as: destination file to save the plot, use .png or .pdf
    :param node_size: the size of the node on the plot
    :param std: this param defines the size of the area that nodes from one district will take on the plot,
                if 0 all nodes from the same district will overlap on the plot
    :param ig_layout: the layout as from ig.Graph.layout() to plot the nodes in a fixed position
    :return: None
    """
    if mode == 'districts':
        for v in graph.vs():
            v['color'] = COLORS[v['district'] % len(COLORS)]
    elif mode == 'states':
        for v in graph.vs():
            v['color'] = COLORS[config.all_states.index(v['state']) % len(COLORS)]
    else:
        raise ValueError(f"Mode '{mode}' not implemented!")

    background = 'white'

    if layout is not None and 'geo' in layout:

        for v in graph.vs():
            v['x'] = (config.district_coords[v['district']][1]) / 180
            v['y'] = (-config.district_coords[v['district']][0]) / 90

        x_min = min(graph.vs()['x'])
        x_max = max(graph.vs()['x'])
        y_min = min(graph.vs()['y'])
        y_max = max(graph.vs()['y'])
        x_diff = x_max - x_min
        y_diff = y_max - y_min

        if layout == 'geo':
            if x_diff > y_diff:
                x_scale = x_diff / y_diff
                y_scale = 1
            else:
                x_scale = 1
                y_scale = y_diff / x_diff
        elif layout == 'geo_strict':
            x_scale = 1
            y_scale = 1
        else:
            raise ValueError(f"Layout '{layout}' not implemented!")

        avg_size = np.mean(config.district_sizes)
        for v in graph.vs():
            v['x'] = v['x'] + normal(0.0, x_scale * std * config.district_sizes[v['district']] / avg_size)
            v['y'] = v['y'] + normal(0.0, y_scale * std * config.district_sizes[v['district']] / avg_size)

        if layout == 'geo_strict':
            diff = max(x_diff, y_diff) / 2
            x_middle = (x_min + x_max) / 2
            y_middle = (y_min + y_max) / 2

            graph.add_vertex(x=x_middle + diff, y=y_middle + diff, color='black')
            graph.add_vertex(x=x_middle - diff, y=y_middle + diff, color='black')
            graph.add_vertex(x=x_middle + diff, y=y_middle - diff, color='black')
            graph.add_vertex(x=x_middle - diff, y=y_middle - diff, color='black')

            background = None

    graph.vs()['size'] = node_size

    if save_as is not None:
        ig.plot(graph, layout=ig_layout, background=background, target=save_as)
    else:
        ig.plot(graph, layout=ig_layout, background=background)
