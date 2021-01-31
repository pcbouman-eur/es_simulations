# -*- coding: utf-8 -*-
import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, '..')
from configuration.parser import get_arguments
from tools import read_data, convert_to_distributions


def density_to_histogram(density, m):
    """
    Function transforms binomial density into a histogram of fractions, with a given number of bins.

    @param density: binomial density of number of votes (states) for '1'. (numpy.array)
    @param m: number of bins in the produced histogram. (int)

    @return: histogram bar sizes obtained from the given density. (numpy.array)
    """
    N = density.shape[0] - 1
    bins = np.linspace(0.0, 1.0, m + 1)
    bins[-1] += 1e-8  # We want 1.0 to be included
    bins_ids = np.digitize(np.arange(N + 1) / N, bins)

    hist = np.zeros(m)
    for i in range(1, m + 1):
        hist[i - 1] = density[bins_ids == i].sum() / (bins[1] - bins[0])

    return hist


def get_binom_hist(config_args, m, system):
    """
    Returns histogram of fractions for binomial approximation, for a given set of parameters.

    @param config_args: set of parameters.
    @param m: number of bins in the produced histogram. (int)
    @param system: electoral system name. (string)

    @return: histogram bar sizes for a given setting in a binomial approximation. (numpy.array)
    """
    p = 0.5 * (1.0 - config_args.EPS) + config_args.EPS * config_args.MASS_MEDIA  # effective state '1' probability
    if system == 'population':
        eff_N = config_args.N - config_args.n_zealots  # number of non-zealot voters
        sub_density = st.binom(eff_N, p).pmf(np.arange(eff_N + 1))  # density for single voters
        density = np.zeros(config_args.N + 1)  # density including zealots
        density[config_args.n_zealots:] = sub_density
        hist = density_to_histogram(density, m)
    elif system == 'district':
        n_d = config_args.N / config_args.q  # number of voters per district
        n_z = config_args.n_zealots / config_args.q  # average number of zealots per district

        # In contrast to the 'population' case, here we only approximate the effect of zealots.
        # Otherwise, we would need to sum over all possible combinations.
        if n_d % 2:
            p_d = 1.0 - st.binom(n_d - n_z, p).cdf(n_d // 2 - n_z)  # probability of winning in a district
        else:
            p_d = 1.0 - st.binom(n_d - n_z, p).cdf(n_d / 2 - n_z) + st.binom(n_d - n_z, p).pmf(n_d / 2 - n_z) * 0.5
        density_d = st.binom(config_args.q, p_d).pmf(np.arange(config_args.q + 1))  # density for districts
        hist = density_to_histogram(density_d, m)
    else:
        raise Exception('Electoral system unknown or not supported for binomial approximation.')
    return hist


def plot_hist_with_binom_approx(distribution, m, hist, name, colors=('tomato', 'mediumseagreen', 'cornflowerblue')):
    """
    Plots a histogram with results of the simulation and binomial approximation on top of that.

    @param distribution: sample of fractions for each state. (dict)
    @param m: number of bins in the produced histogram. (int)
    @param hist: histogram bar sizes of a binomial approximation. (numpy.array)
    @param name: name of the saved figure. (string)
    @param colors: set of colors to be used in the plot. (tuple)
    """
    for idx, key in enumerate(sorted(distribution.keys())):
        col = colors[idx % len(colors)]
        distr = distribution[key]
        bins = np.linspace(0.0, 1.0, m + 1)
        xs = (bins[:-1] + bins[1:]) / 2.0

        plt.figure(figsize=(4, 3))
        plt.hist(distr, bins=bins, range=(0, 1), density=True, color=col)
        if key == '1':
            plt.plot(xs, hist, 'xr')
        else:
            plt.plot(xs, np.flip(hist), 'xr')

        avg = np.mean(distr)
        std = np.std(distr)
        plt.axvline(avg, linestyle='-', color='black')
        plt.axvline(avg - std, linestyle='--', color='black')
        plt.axvline(avg + std, linestyle='--', color='black')

        plt.title('Histogram of seats share, avg={}, std={}'.format(round(avg, 2), round(std, 2)))
        plt.xlabel('fraction of seats')
        plt.ylabel('probability')

        plt.tight_layout()
        plt.savefig(f'plots/{name}.pdf')


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.getcwd()))
    cfg = get_arguments()  # reading arguments
    if cfg.cmd_args.abc:
        raise Exception("Argument 'abc' is not supported for binomial approximation.")
    if cfg.cmd_args.where_zealots != 'random':
        raise Exception("Non random zealots are not supported for binomial approximation.")

    m = 20  # number of bins in the histogram

    res, _ = read_data(cfg.suffix)  # loading data
    for system in ['population', 'district']:
        distribution = convert_to_distributions(res[system])
        hist = get_binom_hist(cfg.cmd_args, m, system)

        s = 'binom_approx_' + system + cfg.suffix
        plot_hist_with_binom_approx(distribution, m, hist, s)
