import matplotlib as mpl
mpl.use('agg')
import os
import sys
import json
import inspect
import numpy as np
from matplotlib import pyplot as plt

# path hack for imports to work when running this script from any location,
# without the hack one has to manually edit PYTHONPATH every time
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from configuration.parser import get_arguments
from configuration.logging import log
from tools import convert_to_distributions, save_data, read_data, run_with_time, calculate_indexes, compute_edge_ratio
from plotting import plot_mean_std, plot_heatmap, plot_std, plot_mean_per, plot_mean_diff, plot_mean_std_all, COLORS


def plot_hist(distribution, bins_num=21, color='blue', key='a'):
    distr = distribution[key]

    plt.hist(distr, bins=np.linspace(0.0, 1.0, bins_num), range=(0, 1), density=True, color=color, alpha=0.7)

    avg = np.mean(distr)
    std = np.std(distr)
    plt.axvline(avg, linestyle='--', color='black', linewidth=0.7)
    # plt.axvline(avg - std, linestyle='--', color='black', linewidth=0.8)
    # plt.axvline(avg + std, linestyle='--', color='black', linewidth=0.8)

    return avg


def main():
    os.chdir(parentdir)
    cfg = get_arguments()
    for key, value in cfg._cmd_args.items():
        log.info(' = '.join([key, str(value)]))

    res, _ = read_data(cfg.suffix)
    # voting_distribution = convert_to_distributions(res['vote_fractions'])

    os.makedirs('plots/', exist_ok=True)

    plt.figure(figsize=(4, 3))
    ax = plt.gca()

    avg = [0, 0]
    for system in cfg.voting_systems.keys():
        distribution = convert_to_distributions(res[system])
        if system == '100 districts FPTP':
            avg[0] = plot_hist(distribution, bins_num=26, color='orangered')
        elif system == 'main_district_system':
            avg[1] = plot_hist(distribution, bins_num=26, color='deepskyblue')

        # indexes = calculate_indexes(voting_distribution, distribution, cfg.sample_size)
        # plot_indexes(indexes, system, cfg.suffix)

    plt.text(0.75, 0.92, 'diff. avg={}'.format(round(avg[0] - avg[1], 2)),
             horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=9)

    plt.title("no zealots")

    plt.xlabel('fraction of seats')
    plt.ylabel('probability')

    plt.tight_layout()
    plt.savefig('plots/seat_dist_z' + cfg.suffix + '.pdf')


if __name__ == '__main__':
    main()
