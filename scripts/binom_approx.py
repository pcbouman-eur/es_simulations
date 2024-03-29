# -*- coding: utf-8 -*-
import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt
import os
import sys
import inspect

# path hack for imports to work when running this script from any location,
# without the hack one has to manually edit PYTHONPATH every time
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from configuration.parser import get_arguments
from tools import read_data, convert_to_distributions

# parameters of simulations not present in the config module
m = 20  # the number of bins in the histogram


def density_to_histogram(density, m):
    """
    Function transforms binomial density into a histogram of fractions, with a given number of bins.

    @param density: binomial density of number of votes (states) for 'a'. (numpy.array)
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
    p = 0.5 * (1.0 - config_args.epsilon) + config_args.epsilon * config_args.mass_media  # effective state 'a' probability
    if system == 'countrywide_system':
        eff_N = config_args.n - config_args.n_zealots  # number of non-zealot voters
        sub_density = st.binom(eff_N, p).pmf(np.arange(eff_N + 1))  # density for single voters
        density = np.zeros(config_args.n + 1)  # density including zealots
        density[config_args.n_zealots:] = sub_density
        hist = density_to_histogram(density, m)
    elif system == 'main_district_system':
        n_d = config_args.n / config_args.q  # number of voters per district
        n_z = config_args.n_zealots / config_args.q  # average number of zealots per district

        # In contrast to the 'countrywide_system' case, here we only approximate the effect of zealots.
        # Otherwise, we would need to sum over all possible combinations.
        if n_d % 2:
            p_d = 1.0 - st.binom(n_d - n_z, p).cdf(n_d // 2 - n_z)  # probability of winning in a district
        else:
            p_d = 1.0 - st.binom(n_d - n_z, p).cdf(n_d // 2 - n_z) + st.binom(n_d - n_z, p).pmf(n_d // 2 - n_z) * 0.5
        density = st.binom(config_args.q, p_d).pmf(np.arange(config_args.q + 1))  # density for districts
        hist = density_to_histogram(density, m)
    else:
        raise Exception('Electoral system unknown or not supported for binomial approximation.')
    return hist, density


def trinom_win_prob(n_d, n_z, p):
    """
    Returns the trinomial approximation for the probability of winning the elections
    given the number of voters "n_d", number of zealots "n_z" and the voting probability "p"
    in a three party system.

    @param n_d: number of voters. (int)
    @param n_z: number of zealots. (int)
    @param p: probability distribution of votes among three parties. (numpy.array)

    @return: winning probability. (float)
    """
    if n_z >= n_d:
        return 1.0

    x = max(0, n_d // 3 - n_z + 1)  # the smallest possible number of votes needed to win
    # first we need to compute the possible losing votes for the second party, given "x"
    temp_col_2 = np.arange(max(0, n_d - 2*x - 2*n_z + 1), min(x + n_z, n_d - x - n_z + 1))
    # the third party will simply be reverse since they need to sum to "n_d - n_z - x"
    temp_col_3 = temp_col_2[::-1]
    # finally we repeat "x" for all the winning configurations
    temp_col_1 = np.repeat(x, temp_col_2.shape[0])

    ids = np.array([temp_col_1, temp_col_2, temp_col_3]).T
    for x in np.arange(max(1, n_d // 3 - n_z + 2), n_d - n_z + 1):  # we go over larger possible votes obtained
        # first we need to compute the possible losing votes for the second party, given "x"
        temp_col_2 = np.arange(max(0, n_d - 2*x - 2*n_z + 1), min(x + n_z, n_d - x - n_z + 1))
        # the third party will simply be reverse since they need to sum to "n_d - n_z - x"
        temp_col_3 = temp_col_2[::-1]
        # finally we repeat "x" for all the winning configurations
        temp_col_1 = np.repeat(x, temp_col_2.shape[0])
        
        temp_ids = np.array([temp_col_1, temp_col_2, temp_col_3]).T  # set of all winning configurations given "x"
        ids = np.concatenate([ids, temp_ids])  # we add the newly computed winning configurations

    return st.multinomial(n_d - n_z, p).pmf(ids).sum()  # we sum over all winning configurations


def trinom_draw_prob(n_d, n_z, p):
    """
    Returns the trinomial approximation for the probability of winning the elections by a draw
    given the number of voters "n_d", number of zealots "n_z" and the voting probability "p"
    in a three party system.

    @param n_d: number of voters. (int)
    @param n_z: number of zealots. (int)
    @param p: probability distribution of votes among three parties. (numpy.array)

    @return: winning by a draw probability. (float)
    """
    if n_z > n_d // 2:
        return 0.0

    # minimum number of votes needed to win by a (non-complete) draw
    x_min = max(0, n_d // 3 - n_z + 1)
    # maximum number of votes that allow to win by a (non-complete) draw
    x_max = n_d // 2 - n_z
    # we compute the possible drawing votes with the second party
    col_1 = np.arange(x_min, x_max+1)
    col_2 = col_1 + n_z
    col_3 = n_d - 2.0 * col_2

    ids_2 = np.array([col_1, col_2, col_3]).T
    ids_3 = np.array([col_1, col_3, col_2]).T
    # Note that in case of a draw the probability of winning is equal to 0.5,
    # however, one can symmetrically draw with 3 party, which means that
    # in the end the correct probability is equal to:
    p_d = 0.5 * (st.multinomial(n_d - n_z, p).pmf(ids_2).sum() +
                 st.multinomial(n_d - n_z, p).pmf(ids_3).sum())

    if n_d % 3:  # we must also include all parties draw
        p_d += st.multinomial(n_d - n_z, p).pmf(np.array([n_d // 3 - n_z,
                                                          n_d // 3,
                                                          n_d // 3])) / 3.0

    return p_d


def get_trinom_hist(config_args, m, system):
    """
    Returns histogram of fractions for trinomial approximation, for a given set of parameters.

    @param config_args: set of parameters.
    @param m: number of bins in the produced histogram. (int)
    @param system: electoral system name. (string)

    @return: histogram bar sizes for a given setting in a binomial approximation. (numpy.array)
    """
    p = np.zeros(3)
    p[0] = (1.0 - config_args.epsilon) / 3.0 + config_args.epsilon * config_args.mass_media  # effective state 'a' probability
    p[1] = (1.0 - p[0]) / 2.0
    p[2] = p[1]
    if system == 'countrywide_system':
        eff_N = config_args.n - config_args.n_zealots  # number of non-zealot voters
        sub_density = st.binom(eff_N, p[0]).pmf(np.arange(eff_N + 1))  # density for single voters
        density = np.zeros(config_args.n + 1)  # density including zealots
        density[config_args.n_zealots:] = sub_density
        hist = density_to_histogram(density, m)
    elif system == 'main_district_system':
        n_d = config_args.n / config_args.q  # number of voters per district
        n_z = config_args.n_zealots / config_args.q  # average number of zealots per district

        # In contrast to the 'countrywide_system' case, here we only approximate the effect of zealots.
        # Otherwise, we would need to sum over all possible combinations.
        p_d = trinom_win_prob(n_d, n_z, p)  # winning probability without draws
        p_d += trinom_draw_prob(n_d, n_z, p)  # winning draw probability

        density = st.binom(config_args.q, p_d).pmf(np.arange(config_args.q + 1))  # density for districts
        hist = density_to_histogram(density, m)
    else:
        raise Exception('Electoral system unknown or not supported for trinomial approximation.')
    return hist, density


def plot_hist_with_binom_approx(distribution, m, hist, density, suffix, colors=('tomato', 'mediumseagreen', 'cornflowerblue')):
    """
    Plots a histogram with results of the simulation and binomial approximation on top of that.

    @param distribution: sample of fractions for each state. (dict)
    @param m: number of bins in the produced histogram. (int)
    @param hist: histogram bar sizes of a binomial approximation. (numpy.array)
    @param density: exact density of a binomial approximation. (numpy.array)
    @param suffix: suffix with parameters for the name of the saved figure. (string)
    @param colors: set of colors to be used in the plot. (tuple)
    """
    for idx, key in enumerate(sorted(distribution.keys())):
        name = 'binom_approx_' + key + '_' + suffix

        col = colors[idx % len(colors)]
        distr = distribution[key]
        bins = np.linspace(0.0, 1.0, m + 1)
        xs = (bins[:-1] + bins[1:]) / 2.0

        N = density.shape[0]

        plt.figure(figsize=(4, 3))
        plt.hist(distr, bins=bins, range=(0, 1), density=True, color=col)
        if key == 'a':
            plt.plot(xs, hist, 'xr')
            plt.plot(np.linspace(0.0, 1.0, N), N * density)
        else:
            plt.plot(xs, np.flip(hist), 'xr')
            plt.plot(np.linspace(0.0, 1.0, N), N * np.flip(density))

        avg = np.mean(distr)
        std = np.std(distr)
        plt.axvline(avg, linestyle='-', color='black')
        plt.axvline(avg - std, linestyle='--', color='black')
        plt.axvline(avg + std, linestyle='--', color='black')

        plt.title('Histogram of seats share, avg={}, std={}'.format(round(avg, 2), round(std, 2)))
        plt.xlabel('fraction of seats')
        plt.ylabel('probability')

        plt.tight_layout()
        plt.savefig(f'plots/{name}.png')


if __name__ == '__main__':
    os.chdir(parentdir)
    cfg = get_arguments()  # reading arguments
    if cfg.num_parties > 2:
        raise ValueError("More than 2 parties are not supported for binomial approximation.")
    if cfg.where_zealots != 'random':
        raise ValueError("Non random zealots are not supported for binomial approximation.")

    try:
        res, _ = read_data(cfg.suffix)  # loading data
    except (OSError, IOError) as e:
        raise IOError("Data for the given configuration was not found, "
                      "run main.py with the same configuration first.")
    for system in ['countrywide_system', 'main_district_system']:
        distribution = convert_to_distributions(res[system])
        hist, density = get_binom_hist(cfg, m, system)

        s = system + cfg.suffix
        plot_hist_with_binom_approx(distribution, m, hist, density, s)
