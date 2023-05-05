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
from tools import convert_to_distributions, read_data
from plotting_scripts.plotting_tools import names_dict


def get_binom_hist(config_args, system):
    p = 1.0/3.0
    if system == 'countrywide_system':
        sub_density = st.binom(config_args.n, p).pmf(np.arange(config_args.n + 1))
        density = np.zeros(config_args.n + 1)
        density[config_args.n_zealots:] = sub_density
    else:
        n_d = config_args.n / config_args.q
        p_d = 1.0 - st.binom(n_d, p).cdf(n_d / 2.8571)
        density = st.binom(config_args.q, p_d).pmf(np.arange(config_args.q + 1))
    return density


def plot_small_seats_hist(dist, file_name=None, number=None, title=None, xlim=None, ylim=None, color=None, bins=26,
                          density=None, text=None):
    plt.figure(figsize=(2.8, 2.4))
    plt.hist(dist, bins=np.linspace(xlim[0], xlim[1], bins), range=(0, 1), density=True, color=color)

    avg = np.mean(dist)
    std = np.std(dist)
    plt.axvline(avg, linestyle='-', color='black', linewidth=0.9, zorder=0)
    plt.axvline(avg - std, linestyle='--', color='black', linewidth=0.8, zorder=0)
    plt.axvline(avg + std, linestyle='--', color='black', linewidth=0.8, zorder=0)

    plt.fill_between([avg - std, avg + std], [ylim[1], ylim[1]], color='#cccccc', zorder=-10)

    if density is not None:
        plt.plot(np.linspace(0.0, 1.0, density.shape[0]), density.shape[0] * density, ls='-', lw=0.9, color='black')

    if text is not None:
        ax = plt.gca()
        plt.text(0.835, 0.865, text, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)

    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.xlabel('fraction of seats')
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

    ylim = [0, 7]
    systems = ['countrywide_system', 'main_district_system', '100 districts Webster', '100 districts FPTP']

    ##########################
    # plot normal case
    cfg = Config(args, parser._option_string_actions)
    res, settings = read_data(cfg.suffix, input_dir='results/final1/')
    numbers = ['a', 'e', 'i', 'm']
    for i, system in enumerate(systems):
        distribution = convert_to_distributions(res[system])
        short = names_dict[system]['short']
        color = names_dict[system]['color']

        plot_small_seats_hist(distribution['a'], number=numbers[i], title=short, ylim=ylim, xlim=[0, 1], color=color,
                              file_name=f'ex_normal_{short.lower()}.pdf')

    ##########################
    # plot random districts
    res, settings = read_data(cfg.suffix, input_dir='results/final3/random_dist/')
    numbers = ['c', 'g', 'k', 'o']
    for i, system in enumerate(systems):
        distribution = convert_to_distributions(res[system])
        short = names_dict[system]['short']
        color = names_dict[system]['color']

        plot_small_seats_hist(distribution['a'], number=numbers[i], title=short, ylim=ylim, xlim=[0, 1], color=color,
                              file_name=f'ex_dist_{short.lower()}.pdf', text='random\ndistricts')

    ##########################
    # plot random graph, i.e. ratio=1
    setattr(args, 'ratio', 1.0)
    cfg = Config(args, parser._option_string_actions)
    res, settings = read_data(cfg.suffix, input_dir='results/final3/')
    numbers = ['b', 'f', 'j', 'n']
    for i, system in enumerate(systems):
        distribution = convert_to_distributions(res[system])
        short = names_dict[system]['short']
        color = names_dict[system]['color']

        plot_small_seats_hist(distribution['a'], number=numbers[i], title=short, ylim=ylim, xlim=[0, 1], color=color,
                              file_name=f'ex_ratio_{short.lower()}.pdf', text=r'$r=1$')

    ##########################
    # plot epsilon=1
    setattr(args, 'ratio', 0.002)
    setattr(args, 'epsilon', 1.0)
    cfg = Config(args, parser._option_string_actions)
    res, settings = read_data(cfg.suffix, input_dir='results/final3/')
    numbers = ['d', 'h', 'l', 'p']
    for i, system in enumerate(systems):
        distribution = convert_to_distributions(res[system])
        short = names_dict[system]['short']
        color = names_dict[system]['color']

        if short == 'PV':
            xlim = [0.18, 0.5]
            bins = 34
        else:
            xlim = [0.3333-0.038, 0.3333+0.038]
            bins = 39

        if system in ['countrywide_system', '100 districts FPTP']:
            density = get_binom_hist(cfg, system)
        else:
            density = None
        if system == '100 districts FPTP':
            ylim = [0, 10]
        else:
            ylim = [0, 90]
        plot_small_seats_hist(distribution['a'], number=numbers[i], title=short, ylim=ylim, xlim=xlim, text=r'$\varepsilon=1$',
                              color=color, bins=bins, file_name=f'ex_epsilon_{short.lower()}.pdf', density=density)


if __name__ == '__main__':
    main()
