# -*- coding: utf-8 -*-
"""
A collection of plotting functions used to generate figures
"""
import os
import numpy as np
from matplotlib import pyplot as plt


COLORS = ('tomato', 'mediumseagreen', 'cornflowerblue')


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
    plt.savefig('{}/trajectory{}.pdf'.format(output_dir, suffix))


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
        plt.savefig(output_dir + name + '_' + str(key) + suffix + '.pdf')


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
