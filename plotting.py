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
COLORS_MANY = ['#B0171F', '#DC143C', '#FFB6C1', '#FFAEB9', '#EEA2AD', '#CD8C95', '#8B5F65', '#FFC0CB', '#FFB5C5',
               '#EEA9B8', '#CD919E', '#8B636C', '#DB7093', '#FF82AB', '#EE799F', '#CD6889', '#8B475D', '#FFF0F5',
               '#EEE0E5', '#CDC1C5', '#8B8386', '#FF3E96', '#EE3A8C', '#CD3278', '#8B2252', '#FF69B4', '#FF6EB4',
               '#EE6AA7', '#CD6090', '#8B3A62', '#872657', '#FF1493', '#EE1289', '#CD1076', '#8B0A50', '#FF34B3',
               '#EE30A7', '#CD2990', '#8B1C62', '#C71585', '#D02090', '#DA70D6', '#FF83FA', '#EE7AE9', '#CD69C9',
               '#8B4789', '#D8BFD8', '#FFE1FF', '#EED2EE', '#CDB5CD', '#8B7B8B', '#FFBBFF', '#EEAEEE', '#CD96CD',
               '#8B668B', '#DDA0DD', '#EE82EE', '#FF00FF', '#EE00EE', '#CD00CD', '#8B008B', '#800080', '#BA55D3',
               '#E066FF', '#D15FEE', '#B452CD', '#7A378B', '#9400D3', '#9932CC', '#BF3EFF', '#B23AEE', '#9A32CD',
               '#68228B', '#4B0082', '#8A2BE2', '#9B30FF', '#912CEE', '#7D26CD', '#551A8B', '#9370DB', '#AB82FF',
               '#9F79EE', '#8968CD', '#5D478B', '#483D8B', '#8470FF', '#7B68EE', '#6A5ACD', '#836FFF', '#7A67EE',
               '#6959CD', '#473C8B', '#F8F8FF', '#E6E6FA', '#0000FF', '#0000EE', '#0000CD', '#00008B', '#000080',
               '#191970', '#3D59AB', '#4169E1', '#4876FF', '#436EEE', '#3A5FCD', '#27408B', '#6495ED', '#B0C4DE',
               '#CAE1FF', '#BCD2EE', '#A2B5CD', '#6E7B8B', '#778899', '#708090', '#C6E2FF', '#B9D3EE', '#9FB6CD',
               '#6C7B8B', '#1E90FF', '#1C86EE', '#1874CD', '#104E8B', '#F0F8FF', '#4682B4', '#63B8FF', '#5CACEE',
               '#4F94CD', '#36648B', '#87CEFA', '#B0E2FF', '#A4D3EE', '#8DB6CD', '#607B8B', '#87CEFF', '#7EC0EE',
               '#6CA6CD', '#4A708B', '#87CEEB', '#00BFFF', '#00B2EE', '#009ACD', '#00688B', '#33A1C9', '#ADD8E6',
               '#BFEFFF', '#B2DFEE', '#9AC0CD', '#68838B', '#B0E0E6', '#98F5FF', '#8EE5EE', '#7AC5CD', '#53868B',
               '#00F5FF', '#00E5EE', '#00C5CD', '#00868B', '#5F9EA0', '#00CED1', '#F0FFFF', '#E0EEEE', '#C1CDCD',
               '#838B8B', '#E0FFFF', '#D1EEEE', '#B4CDCD', '#7A8B8B', '#BBFFFF', '#AEEEEE', '#96CDCD', '#668B8B',
               '#2F4F4F', '#97FFFF', '#8DEEEE', '#79CDCD', '#528B8B', '#00FFFF', '#00EEEE', '#00CDCD', '#008B8B',
               '#008080', '#48D1CC', '#20B2AA', '#03A89E', '#40E0D0', '#808A87', '#00C78C', '#7FFFD4', '#76EEC6',
               '#66CDAA', '#458B74', '#00FA9A', '#F5FFFA', '#00FF7F', '#00EE76', '#00CD66', '#008B45', '#3CB371',
               '#54FF9F', '#4EEE94', '#43CD80', '#2E8B57', '#00C957', '#BDFCC9', '#3D9140', '#F0FFF0', '#E0EEE0',
               '#C1CDC1', '#838B83', '#8FBC8F', '#C1FFC1', '#B4EEB4', '#9BCD9B', '#698B69', '#98FB98', '#9AFF9A',
               '#90EE90', '#7CCD7C', '#548B54', '#32CD32', '#228B22', '#00FF00', '#00EE00', '#00CD00', '#008B00',
               '#008000', '#006400', '#308014', '#7CFC00', '#7FFF00', '#76EE00', '#66CD00', '#458B00', '#ADFF2F',
               '#CAFF70', '#BCEE68', '#A2CD5A', '#6E8B3D', '#556B2F', '#6B8E23', '#C0FF3E', '#B3EE3A', '#9ACD32',
               '#698B22', '#FFFFF0', '#EEEEE0', '#CDCDC1', '#8B8B83', '#F5F5DC', '#FFFFE0', '#EEEED1', '#CDCDB4',
               '#8B8B7A', '#FAFAD2', '#FFFF00', '#EEEE00', '#CDCD00', '#8B8B00', '#808069', '#808000', '#BDB76B',
               '#FFF68F', '#EEE685', '#CDC673', '#8B864E', '#F0E68C', '#EEE8AA', '#FFFACD', '#EEE9BF', '#CDC9A5',
               '#8B8970', '#FFEC8B', '#EEDC82', '#CDBE70', '#8B814C', '#E3CF57', '#FFD700', '#EEC900', '#CDAD00',
               '#8B7500', '#FFF8DC', '#EEE8CD', '#CDC8B1', '#8B8878', '#DAA520', '#FFC125', '#EEB422', '#CD9B1D',
               '#8B6914', '#B8860B', '#FFB90F', '#EEAD0E', '#CD950C', '#8B6508', '#FFA500', '#EE9A00', '#CD8500',
               '#8B5A00', '#FFFAF0', '#FDF5E6', '#F5DEB3', '#FFE7BA', '#EED8AE', '#CDBA96', '#8B7E66', '#FFE4B5',
               '#FFEFD5', '#FFEBCD', '#FFDEAD', '#EECFA1', '#CDB38B', '#8B795E', '#FCE6C9', '#D2B48C', '#9C661F',
               '#FF9912', '#FAEBD7', '#FFEFDB', '#EEDFCC', '#CDC0B0', '#8B8378', '#DEB887', '#FFD39B', '#EEC591',
               '#CDAA7D', '#8B7355', '#FFE4C4', '#EED5B7', '#CDB79E', '#8B7D6B', '#E3A869', '#ED9121', '#FF8C00',
               '#FF7F00', '#EE7600', '#CD6600', '#8B4500', '#FF8000', '#FFA54F', '#EE9A49', '#CD853F', '#8B5A2B',
               '#FAF0E6', '#FFDAB9', '#EECBAD', '#CDAF95', '#8B7765', '#FFF5EE', '#EEE5DE', '#CDC5BF', '#8B8682',
               '#F4A460', '#C76114', '#D2691E', '#FF7F24', '#EE7621', '#CD661D', '#8B4513', '#292421', '#FF7D40',
               '#FF6103', '#8A360F', '#A0522D', '#FF8247', '#EE7942', '#CD6839', '#8B4726', '#FFA07A', '#EE9572',
               '#CD8162', '#8B5742', '#FF7F50', '#FF4500', '#EE4000', '#CD3700', '#8B2500', '#5E2612', '#E9967A',
               '#FF8C69', '#EE8262', '#CD7054', '#8B4C39', '#FF7256', '#EE6A50', '#CD5B45', '#8B3E2F', '#8A3324',
               '#FF6347', '#EE5C42', '#CD4F39', '#8B3626', '#FA8072', '#FFE4E1', '#EED5D2', '#CDB7B5', '#8B7D7B',
               '#FFFAFA', '#EEE9E9', '#CDC9C9', '#8B8989', '#BC8F8F', '#FFC1C1', '#EEB4B4', '#CD9B9B', '#8B6969',
               '#F08080', '#CD5C5C', '#FF6A6A', '#EE6363', '#8B3A3A', '#CD5555', '#A52A2A', '#FF4040', '#EE3B3B',
               '#CD3333', '#8B2323', '#B22222', '#FF3030', '#EE2C2C', '#CD2626', '#8B1A1A', '#FF0000', '#EE0000',
               '#CD0000', '#8B0000', '#800000', '#8E388E', '#7171C6', '#7D9EC0', '#388E8E', '#71C671', '#8E8E38',
               '#C5C1AA', '#C67171']


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
        ax = plt.gca()

        plt.hist(distr, bins=np.linspace(0.0, 1.0, bins_num), range=(0, 1), density=True, color=col)

        avg = np.mean(distr)
        std = np.std(distr)
        plt.axvline(avg, linestyle='-', color='black', linewidth=0.9)
        plt.axvline(avg - std, linestyle='--', color='black', linewidth=0.8)
        plt.axvline(avg + std, linestyle='--', color='black', linewidth=0.8)

        plt.text(0.75, 0.92, 'avg={}, std={}'.format(round(avg, 2), round(std, 2)),
                 horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=9)
        plt.xlabel('fraction of seats')
        plt.ylabel('probability')

        plt.tight_layout()
        plt.savefig(output_dir + name + '_' + str(key) + suffix + '.png')
        plt.close('all')


def plot_indexes(indexes, name, suffix, output_dir='plots/', colors=('mediumorchid', 'gold', 'deepskyblue')):
    for idx, (index, values) in enumerate(indexes.items()):
        col = colors[idx % len(colors)]

        lim0 = np.min([0, np.min(values)])
        lim1 = np.max([1, np.max(values)])

        plt.figure(figsize=(4, 3))
        ax = plt.gca()

        plt.hist(values, bins=np.linspace(lim0, lim1, 21), range=(0, 1), density=True, color=col)

        avg = np.mean(values)
        std = np.std(values)
        plt.axvline(avg, linestyle='-', color='black', linewidth=0.9)
        plt.axvline(avg - std, linestyle='--', color='black', linewidth=0.8)
        plt.axvline(avg + std, linestyle='--', color='black', linewidth=0.8)

        plt.text(0.5, 0.92, f'avg={round(avg, 2)}\nstd={round(std, 2)}',
                 horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=9)
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
                      save_file=True, vline=None):
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
    :param vline: position of a vertical line to add
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

    if vline is not None:
        plt.axvline(vline, linewidth=0.6, linestyle='--', color='black')

    plt.title(f'{quantity} susceptibility')
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.legend(fontsize=8)
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


def plot_network(graph, config, mode='districts', layout='geo', save_as=None, node_size=10, std=0.00015,
                 ig_layout=None, colors=COLORS_MANY, no_background=False):
    """
    Plotting igraph.Graph() object in various ways, indicating with color districts or states of the nodes.
    :param graph: the network to plot, igraph.Graph() object
    :param config: configuration of the simulation, config.Config() object
    :param mode: either 'districts' to color the nodes according to their districts, or 'states' according to parties
    :param layout: 'default', 'geo', or 'geo_strict', the mode of plotting the net, if None it'll be default from iGraph
    :param save_as: destination file to save the plot, use .png or .pdf
    :param node_size: the size of the node on the plot
    :param std: this param defines the size of the area that nodes from one district will take on the plot,
                if 0 all nodes from the same district will overlap on the plot
    :param ig_layout: the layout as from ig.Graph.layout() to plot the nodes in a fixed position
    :param colors: list of colours to use when plotting districts
    :param no_background: if True, background is transparent instead of white
    :return: None
    """
    if mode == 'districts':
        for v in graph.vs():
            v['color'] = colors[v['district'] % len(colors)]
            v['frame_color'] = '#404040'
    elif mode == 'states':
        for v in graph.vs():
            v['color'] = COLORS[config.all_states.index(v['state']) % len(COLORS)]
    else:
        raise ValueError(f"Mode '{mode}' not implemented!")

    if no_background:
        background = None
    else:
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

            graph.add_vertex(x=x_middle + diff, y=y_middle + diff, color='white', frame_color='white')
            graph.add_vertex(x=x_middle - diff, y=y_middle + diff, color='white', frame_color='white')
            graph.add_vertex(x=x_middle + diff, y=y_middle - diff, color='white', frame_color='white')
            graph.add_vertex(x=x_middle - diff, y=y_middle - diff, color='white', frame_color='white')

    graph.vs()['size'] = node_size
    graph.es()['width'] = 0.5
    graph.es()['color'] = '#404040'

    if save_as is not None:
        ig.plot(graph, layout=ig_layout, background=background, target=save_as, bbox=(1000, 1000))
    else:
        ig.plot(graph, layout=ig_layout, background=background, bbox=(1000, 1000))
