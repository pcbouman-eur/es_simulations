#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# libraries
import json
import numpy as np
import matplotlib.pyplot as plt

# set parameters of simulations
zn_set = range(61) #range of considered nuber of zealots
N = str(1875)
q = str(25)
EPS = str(0.01)
S = str(1000)
T = str(300000)
R = str(0.1)
p = 'standard'
l_bins_hist_pop = 100 #how many bins in histogram of population
l_bins_hist_dist = np.int64(q) #how many bins in histogram of districts

# funcions
def convert_to_distribution(series, missing_value=0):
    """
    Converts a loaded JSON data to array
    """
    # Compute all keys that occur in the series
    keys = set()
    for d in series:
        keys.update(d.keys())
    res = {k: [d[k] if np.isin(k, list(d)) else missing_value for d in series] for k in keys}
    return res

def plot_mean_std(y, ylab, std, name, x = zn_set, xlab = 'Number of zealots', save_file = True):
    """
    Plots a plot of mean +/- std of given variable vs number of zealots 
    :param y: given variable
    :param ylab: y-axis label
    :param std: standard deviation of y
    :param name: name of quantity (Population or District)
    :param x: array with number of zealots
    :param xlab: x-axis label
    :param save_file: bool if save plot to file
    """
    plt.figure()

    plt.plot(x, y, color = 'black', linestyle = '-')
    plt.plot(x, y + std, color = 'black', linestyle = '--')
    plt.plot(x, y - std, color = 'black', linestyle = '--')
    
    plt.title(name)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.tight_layout()
    if save_file:
        plt.savefig('plots/' + name + '_Mean' + suffix + '.pdf')
    else:
        plt.show()

def plot_heatmap(heatmap, l_bins, ylab, name, xlab = 'Number of zealots', save_file = True, colormap = 'viridis'):
    """
    Plots a heatmap of given variable vs number of zealots 
    :param heatmap: histogram of given variable
    :param ylab: y-axis label
    :param name: name of quantity (Population or District)
    :param xlab: x-axis label
    :param save_file: bool if save plot to file
    :param colormap: change colormap
    """
    plot_heatmap = np.transpose(heatmap)
    plot_heatmap /= np.sum(plot_heatmap, 0)
    
    plt.figure(figsize = (5, 5))
    
    plt.imshow(plot_heatmap, origin = 'lower', aspect='auto', cmap = colormap)
    plt.colorbar()
    
    plt.title(name)
    plt.yticks(np.linspace(0, l_bins, 5)-0.5 , np.linspace(0, 1, 5))
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.tight_layout()
    if save_file:
        plt.savefig('plots/' + name + '_Heatmap' + suffix + '.pdf')
    else:
        plt.show()

# create variables for data
suffix = '_N_{}_q_{}_EPS_{}_S_{}_T_{}_R_{}_p_{}'.format(N, q, EPS, S, T, R, p)
loc1 = 'results/results'
loc2 = '.json'
l_zn_set = len(zn_set)
bins_hist_pop = np.linspace(0, 1, num = l_bins_hist_pop + 1)
pop_mean_set = np.zeros(l_zn_set)
pop_std_set = np.zeros(l_zn_set)
pop_hist_set = np.zeros((l_zn_set, l_bins_hist_pop))
bins_hist_dist = np.linspace(0, 1, num = l_bins_hist_dist + 1)
dist_mean_set = np.zeros(l_zn_set)
dist_std_set = np.zeros(l_zn_set)
dist_hist_set = np.zeros((l_zn_set, l_bins_hist_dist))

# load data
for i, zn in enumerate(zn_set):
    loc = loc1 + suffix + '_zn_' + str(zn) + loc2
    with open(loc) as json_file:
        data = json.load(json_file)
    population_1 = convert_to_distribution(data['results']['population'])['1']
    district_1 = convert_to_distribution(data['results']['district'])['1']
    pop_mean_set[i] = np.mean(population_1)
    pop_std_set[i] = np.std(population_1)
    pop_hist_set[i,:] = np.histogram(population_1, bins = bins_hist_pop)[0]
    dist_mean_set[i] = np.mean(district_1)
    dist_std_set[i] = np.std(district_1)
    dist_hist_set[i,:] = np.histogram(district_1, bins = bins_hist_dist)[0]

# plot figures

plot_mean_std(y = pop_mean_set, ylab = 'Part of population in state 1', std = pop_std_set, name = 'Population')
plot_mean_std(y = dist_mean_set, ylab = 'Part of districts in state 1', std = dist_std_set, name = 'District')
    
plot_heatmap(heatmap = pop_hist_set, l_bins = l_bins_hist_pop, ylab = 'Distribution of population in state 1', name = 'Population')
plot_heatmap(heatmap = dist_hist_set, l_bins = l_bins_hist_dist, ylab = 'Distribution of districts in state 1', name = 'District')
