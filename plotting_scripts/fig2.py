import os
import sys
import inspect
import numpy as np
from matplotlib import pyplot as plt
from collections import defaultdict

# path hack for imports to work when running this script from any location,
# without the hack one has to manually edit PYTHONPATH every time
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from configuration.parser import parser
from configuration.config import Config
from tools import read_data, convert_to_distributions, calculate_indexes
from plotting_scripts.plotting_tools import names_dict, DefDict


cm = 1/2.54  # centimeters in inches


def main():
    os.chdir(parentdir)

    plt.rcParams.update({'font.size': 7})
    title_font = 8

    gs_kw = dict(width_ratios=[1, 1], height_ratios=[1, 1])
    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(8.7*cm, 7.5*cm), gridspec_kw=gs_kw)

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################

    args = parser.parse_args()
    setattr(args, 'n', 10000)
    setattr(args, 'q', 100)
    setattr(args, 'sample_size', 500)
    setattr(args, 'mc_steps', 1000)
    setattr(args, 'therm_time', 1)
    setattr(args, 'seats', [5])
    setattr(args, 'ratio', 0.002)
    setattr(args, 'avg_deg', 12.0)
    setattr(args, 'epsilon', 0.005)
    setattr(args, 'num_parties', 3)
    setattr(args, 'short_suffix', True)
    setattr(args, 'n_zealots', 26)
    cfg = Config(args, parser._option_string_actions)
    res, settings = read_data('_basic_z' + cfg.suffix, input_dir='results/final1/')

    for system in ['main_district_system', '100 districts FPTP']:
        distribution = convert_to_distributions(res[system])
        color = 'deepskyblue' if system == 'main_district_system' else 'orangered'
        axs[0, 0].hist(distribution['a'], bins=np.linspace(0.0, 1.0, 25), range=(0, 1), density=True, color=color,
                       alpha=0.7, zorder=10)
        axs[0, 0].axvline(np.mean(distribution['a']), ls='--', lw=0.8, color='black', zorder=0)

    axs[0, 0].axvline(1. / 3, ls='-', lw=0.8, color='black', zorder=0)

    axs[0, 0].set_xlim([0, 1])
    axs[0, 0].set_ylim([0, 6.5])
    axs[0, 0].set_xlabel('fraction of seats')
    axs[0, 0].set_ylabel('probability')
    axs[0, 0].set_title('a', loc='left', fontweight='bold', fontsize=title_font)
    axs[0, 0].set_xticks((0, 1. / 3, 2. / 3, 1))
    axs[0, 0].set_xticklabels((0, 0.33, 0.66, 1))

    axs[0, 0].text(0.12, 3.125, 'PR', bbox=dict(facecolor='deepskyblue', edgecolor='none', pad=2.0, alpha=0.7))
    axs[0, 0].text(0.12, 2.1, 'PV', bbox=dict(facecolor='orangered', edgecolor='none', pad=2.0, alpha=0.7))
    axs[0, 0].set_title(' 0.25% of zealots', fontsize=7)

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################

    args = parser.parse_args()
    setattr(args, 'n', 10000)
    setattr(args, 'q', 100)
    setattr(args, 'sample_size', 500)
    setattr(args, 'mc_steps', 1000)
    setattr(args, 'therm_time', 1)
    setattr(args, 'seats', [5])
    setattr(args, 'ratio', 0.002)
    setattr(args, 'avg_deg', 12.0)
    setattr(args, 'epsilon', 0.005)
    setattr(args, 'num_parties', 3)
    setattr(args, 'short_suffix', True)

    systems = ['100 districts FPTP', 'main_district_system', 'countrywide_system']  # '100 districts Webster'
    systems_res = defaultdict(DefDict)

    z_list = list(range(0, 400, 13))
    for i, z in enumerate(z_list):
        setattr(args, 'n_zealots', z)
        cfg = Config(args, parser._option_string_actions)
        res, settings = read_data('_basic_z' + cfg.suffix, input_dir='results/final1/')
        voting_distribution = convert_to_distributions(res['vote_fractions'])

        for system in systems:
            distribution = convert_to_distributions(res[system])
            systems_res[system]['data'].append(distribution['a'])
            systems_res[system]['mean'].append(np.mean(distribution['a']))
            systems_res[system]['std'].append(np.std(distribution['a']))

            indexes = calculate_indexes(voting_distribution, distribution, cfg.sample_size)
            systems_res[system]['gall'].append(indexes['Gallagher index'])
            systems_res[system]['loos'].append(indexes['Loosemore Hanby index'])
            systems_res[system]['eff'].append(indexes['Eff. No of Parties'])

    axs[0, 1].axhline(1. / 3, ls='--', lw=0.8, color='black', zorder=-10)
    x_list = [100.0 * x / 10000 for x in z_list]

    for system in systems:
        mean = np.array(systems_res[system]['mean'])
        std = np.array(systems_res[system]['std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        axs[0, 1].plot(x_list, mean, color=color, ls='-', label=short, lw=1)
        axs[0, 1].fill_between(x_list, mean - std, mean + std, color=color, lw=0, alpha=0.45)

    axs[0, 1].set_title('b', loc='left', fontweight='bold', fontsize=title_font)
    axs[0, 1].set_xlabel('% of zealots')
    axs[0, 1].set_ylabel('fraction of seats')
    axs[0, 1].legend(loc=4)
    axs[0, 1].set_title(' zealot susceptibility', fontsize=7)

    axs[0, 1].set_xlim([0, z_list[-1] / 100.])
    axs[0, 1].set_ylim([0.3, 1.005])

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################

    args = parser.parse_args()
    setattr(args, 'n', 10000)
    setattr(args, 'q', 100)
    setattr(args, 'sample_size', 500)
    setattr(args, 'mc_steps', 1000)
    setattr(args, 'therm_time', 1)
    setattr(args, 'seats', [5])
    setattr(args, 'ratio', 0.002)
    setattr(args, 'avg_deg', 12.0)
    setattr(args, 'epsilon', 0.005)
    setattr(args, 'num_parties', 3)
    setattr(args, 'short_suffix', True)

    systems_res = defaultdict(lambda: defaultdict(list))
    systems = ['100 districts FPTP', 'main_district_system', 'countrywide_system']  # '100 districts Webster'

    z_list = list(range(0, 400, 13))
    for i, z in enumerate(z_list):
        setattr(args, 'n_zealots', z)
        cfg = Config(args, parser._option_string_actions)
        res, settings = read_data('_basic_z' + cfg.suffix, input_dir='results/final1/')
        voting_distribution = convert_to_distributions(res['vote_fractions'])

        for system in systems:
            distribution = convert_to_distributions(res[system])
            indexes = calculate_indexes(voting_distribution, distribution, cfg.sample_size)
            systems_res[system]['gall_mean'].append(np.mean(indexes['Gallagher index']))
            systems_res[system]['gall_std'].append(np.std(indexes['Gallagher index']))
            systems_res[system]['loos_mean'].append(np.mean(indexes['Loosemore Hanby index']))
            systems_res[system]['loos_std'].append(np.std(indexes['Loosemore Hanby index']))
            systems_res[system]['eff_mean'].append(np.mean(indexes['Eff. No of Parties']))
            systems_res[system]['eff_std'].append(np.std(indexes['Eff. No of Parties']))

    ####################################################################################################################

    x_list = [100.0 * x / 10000 for x in z_list]
    for system in systems:
        mean = np.array(systems_res[system]['gall_mean'])
        std = np.array(systems_res[system]['gall_std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        axs[1, 0].plot(x_list, mean, color=color, ls='-', label=short, lw=1)
        axs[1, 0].fill_between(x_list, mean - std, mean + std, color=color, lw=0, alpha=0.45)

    # axs[1, 0].set_title('disproportionality')
    axs[1, 0].set_title('c', loc='left', fontweight='bold')
    axs[1, 0].set_xlabel('% of zealots')
    axs[1, 0].set_ylabel('Gallagher index')
    axs[1, 0].legend(loc=1)
    axs[1, 0].set_xlim([0, z_list[-1] / 100.])
    axs[1, 0].set_ylim([-0.01, 0.32])

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################

    x_list = [100.0 * x / 10000 for x in z_list]
    for system in systems:
        mean = np.array(systems_res[system]['eff_mean'])
        std = np.array(systems_res[system]['eff_std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        axs[1, 1].plot(x_list, mean, color=color, ls='-', label=short, lw=1)
        axs[1, 1].fill_between(x_list, mean - std, mean + std, color=color, lw=0, alpha=0.45)

    # axs[1, 1].set_title('fragmentation')
    axs[1, 1].set_title('d', loc='left', fontweight='bold')
    axs[1, 1].set_xlabel('% of zealots')
    axs[1, 1].set_ylabel('eff. num. of parties')
    axs[1, 1].legend(loc=1)
    axs[1, 1].set_xlim([0, z_list[-1] / 100.])
    axs[1, 1].set_ylim([0.975, 3.02])

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################

    plt.subplots_adjust(left=0.12, right=0.985, top=0.94, bottom=0.115, hspace=0.58, wspace=0.43)
    plt.savefig(f'plots/fig2.pdf')
    plt.close()


if __name__ == '__main__':
    main()

