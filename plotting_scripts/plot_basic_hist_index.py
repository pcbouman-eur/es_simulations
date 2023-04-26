import os
import sys
import inspect
import numpy as np
from matplotlib import pyplot as plt
import scipy.stats as st

# path hack for imports to work when running this script from any location,
# without the hack one has to manually edit PYTHONPATH every time
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from configuration.parser import parser
from configuration.config import Config
from tools import convert_to_distributions, read_data, calculate_indexes
from plotting_scripts.plotting_tools import names_dict


def plot_small_seats_hist(dist, file_name=None, number=None, title=None, xlim=None, ylim=None, color=None, bins=25,
                          density=None, text=None, xlabel=None):
    plt.figure(figsize=(3.2, 2.6))
    if xlim is not None:
        plt.hist(dist, bins=np.linspace(xlim[0], xlim[1], bins), range=(xlim[0], xlim[1]), density=True, color=color)
    else:
        plt.hist(dist, density=True, color=color)

    avg = np.mean(dist)
    std = np.std(dist)
    plt.axvline(avg, linestyle='-', color='black', linewidth=0.9, zorder=0)
    plt.axvline(avg - std, linestyle='--', color='black', linewidth=0.8, zorder=0)
    plt.axvline(avg + std, linestyle='--', color='black', linewidth=0.8, zorder=0)

    if ylim is not None:
        plt.fill_between([avg - std, avg + std], [ylim[1], ylim[1]], color='#cccccc', zorder=-10)
        plt.ylim(ylim)

    if density is not None:
        plt.plot(np.linspace(0.0, 1.0, density.shape[0]), density.shape[0] * density, ls='-', lw=0.9, color='black')

    if text is not None:
        ax = plt.gca()
        plt.text(0.835, 0.865, text, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)

    plt.xlim(xlim)
    if xlabel is None:
        plt.xlabel('fraction of seats')
    else:
        plt.xlabel(xlabel)
    plt.ylabel('probability')
    plt.title(title)
    plt.title(number, loc='left', fontweight='bold')

    if xlim == [0, 1]:
        ax = plt.gca()
        ax.set_xticks((0, 0.25, 0.5, 0.75, 1))
        ax.set_xticklabels((0, 0.25, 0.5, 0.75, 1))

    plt.tight_layout()
    plt.savefig(f'plots/{file_name}')
    plt.close()


def main():
    os.chdir(parentdir)

    args = parser.parse_args()
    setattr(args, 'n', 10000)
    setattr(args, 'q', 100)
    setattr(args, 'sample_size', 4000)
    setattr(args, 'mc_steps', 50)
    setattr(args, 'therm_time', 10000000)
    setattr(args, 'seats', [5])
    setattr(args, 'ratio', 0.002)
    setattr(args, 'avg_deg', 12.0)
    setattr(args, 'epsilon', 0.005)
    setattr(args, 'num_parties', 3)

    ylim=[0, 7]
    systems = ['countrywide_system', 'main_district_system', '100 districts Webster', '100 districts FPTP']

    cfg = Config(args, parser._option_string_actions)
    res, settings = read_data(cfg.suffix, input_dir='results/final1/')
    voting_distribution = convert_to_distributions(res['vote_fractions'])

    numbers = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o']
    for i, system in enumerate(systems):
        distribution = convert_to_distributions(res[system])
        short = names_dict[system]['short']

        if system == '100 districts FPTP':
            xlim1 = [0, 0.4]
            xlim2 = [1, 3]
            ylim1 = [0, 10]
            ylim2 = [0, 2]
        elif system in ['main_district_system', '100 districts Webster']:
            xlim1 = [0, 0.07]
            xlim2 = [2, 3]
            ylim1 = [0, 120]
            ylim2 = [0, 8]
        else:
            xlim1 = [0, 0.07]
            xlim2 = [2, 3]
            ylim1 = [0, 400]
            ylim2 = [0, 8]

        indexes = calculate_indexes(voting_distribution, distribution, cfg.sample_size)
        plot_small_seats_hist(indexes['Gallagher index'], number=numbers[i*3:][0], title=short, ylim=ylim1, xlim=xlim1,
                              color='mediumorchid', file_name=f'basic_index_{short.lower()}_gall.pdf', xlabel='Gallagher index')
        plot_small_seats_hist(indexes['Loosemore Hanby index'], number=numbers[i*3:][1], title=short, ylim=ylim1, xlim=xlim1,
                              color='darkcyan', file_name=f'basic_index_{short.lower()}_loos.pdf', xlabel='Loosemore-Hanby index')
        plot_small_seats_hist(indexes['Eff. No of Parties'], number=numbers[i*3:][2], title=short, ylim=ylim2, xlim=xlim2,
                              color='darkorange', file_name=f'basic_index_{short.lower()}_eff.pdf', xlabel='effective num. of parties')


if __name__ == '__main__':
    main()

