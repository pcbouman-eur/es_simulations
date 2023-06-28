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


def trinom_draw_prob(n_d, n_z, p):
    """
    copied form scripts/binom_approx.py on master
    """
    if n_z > n_d // 2:
        return 0.0

    x_min = max(0, n_d // 3 - n_z + 1)
    x_max = n_d // 2 - n_z
    col_1 = np.arange(x_min, x_max+1)
    col_2 = col_1 + n_z
    col_3 = n_d - 2.0 * col_2

    ids_2 = np.array([col_1, col_2, col_3]).T
    ids_3 = np.array([col_1, col_3, col_2]).T
    p_d = 0.5 * (st.multinomial(n_d - n_z, p).pmf(ids_2).sum() +
                 st.multinomial(n_d - n_z, p).pmf(ids_3).sum())

    if n_d % 3:
        p_d += st.multinomial(n_d - n_z, p).pmf(np.array([n_d // 3 - n_z, n_d // 3, n_d // 3])) / 3.0
    return p_d


def trinom_win_prob(n_d, n_z, p):
    if n_z >= n_d:
        return 1.0

    x = max(0, n_d // 3 - n_z + 1)
    temp_col_2 = np.arange(max(0, n_d - 2 * x - 2 * n_z + 1), min(x + n_z, n_d - x - n_z + 1))
    temp_col_3 = temp_col_2[::-1]
    temp_col_1 = np.repeat(x, temp_col_2.shape[0])

    ids = np.array([temp_col_1, temp_col_2, temp_col_3]).T
    for x in np.arange(max(1, n_d // 3 - n_z + 2), n_d - n_z + 1):
        temp_col_2 = np.arange(max(0, n_d - 2 * x - 2 * n_z + 1), min(x + n_z, n_d - x - n_z + 1))
        temp_col_3 = temp_col_2[::-1]
        temp_col_1 = np.repeat(x, temp_col_2.shape[0])

        temp_ids = np.array([temp_col_1, temp_col_2, temp_col_3]).T
        ids = np.concatenate([ids, temp_ids])

    return st.multinomial(n_d - n_z, p).pmf(ids).sum()


def get_binom_hist(config_args, system):
    if system == 'countrywide_system':
        p = 1.0 / 3.0
        sub_density = st.binom(config_args.n, p).pmf(np.arange(config_args.n + 1))
        density = np.zeros(config_args.n + 1)
        density[config_args.n_zealots:] = sub_density
    else:
        p = np.zeros(3)
        p[0] = (1.0 - config_args.epsilon) / 3.0 + config_args.epsilon * config_args.mass_media
        p[1] = (1.0 - p[0]) / 2.0
        p[2] = p[1]
        n_d = config_args.n / config_args.q
        n_z = config_args.n_zealots / config_args.q

        p_d = trinom_win_prob(n_d, n_z, p)
        p_d += trinom_draw_prob(n_d, n_z, p)

        density = st.binom(config_args.q, p_d).pmf(np.arange(config_args.q + 1))  # density for districts
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

