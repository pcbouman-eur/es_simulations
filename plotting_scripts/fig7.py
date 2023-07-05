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


names_dict = {
    'main_district_system': {
        'short': '542 dist. PV*',
        'long': 'FPTP with 542 districts',
        'color': 'mediumorchid',
    },
    '36 districts': {
        'short': '36 dist. PR',
        'long': '',
        'color': 'deepskyblue',
    },
    'countrywide_system': {
        'short': '1 dist. PR',
        'long': '',
        'color': 'mediumseagreen',
    },
    '132 districts': {
        'short': '132 dist. PR',
        'long': '',
        'color': 'sandybrown',
    },
    '132 districts FPTP': {
        'short': '132 dist. PV',
        'long': '',
        'color': 'orangered',
    },
}


cm = 1/2.54  # centimeters in inches


def main():
    os.chdir(parentdir)

    plt.rcParams.update({'font.size': 7})
    title_font = 8

    gs_kw = dict(width_ratios=[1, 1], height_ratios=[1.5, 1, 1.5, 1])
    fig, axs = plt.subplots(nrows=4, ncols=2, figsize=(8.7*cm, 17*cm), gridspec_kw=gs_kw)
    gs = axs[0, 0].get_gridspec()
    for ax in axs[0, 0:]:
        ax.remove()
    axbig1 = fig.add_subplot(gs[0, 0:])
    for ax in axs[2, 0:]:
        ax.remove()
    axbig2 = fig.add_subplot(gs[2, 0:])

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################

    args = parser.parse_args()
    setattr(args, 'n', 100000)
    setattr(args, 'mc_steps', 300)
    setattr(args, 'num_parties', 9)
    setattr(args, 'short_suffix', True)

    systems_res = defaultdict(lambda: defaultdict(list))
    systems = ['main_district_system', '132 districts', '132 districts FPTP', '36 districts', 'countrywide_system']

    z_list = list(range(0, 2020, 67))
    for i, z in enumerate(z_list):
        setattr(args, 'n_zealots', z)
        cfg = Config(args, parser._option_string_actions)
        res, settings = read_data('_ind_house_otp' + cfg.suffix, input_dir='results/final3/')
        voting_distribution = convert_to_distributions(res['vote_fractions'])

        for system in systems:
            distribution = convert_to_distributions(res[system])
            systems_res[system]['data'].append(distribution['a'])
            systems_res[system]['mean'].append(np.mean(distribution['a']))
            systems_res[system]['std'].append(np.std(distribution['a']))
            indexes = calculate_indexes(voting_distribution, distribution, settings['sample_size'])
            systems_res[system]['gall_mean'].append(np.mean(indexes['Gallagher index']))
            systems_res[system]['gall_std'].append(np.std(indexes['Gallagher index']))
            systems_res[system]['loos_mean'].append(np.mean(indexes['Loosemore Hanby index']))
            systems_res[system]['loos_std'].append(np.std(indexes['Loosemore Hanby index']))
            systems_res[system]['eff_mean'].append(np.mean(indexes['Eff. No of Parties']))
            systems_res[system]['eff_std'].append(np.std(indexes['Eff. No of Parties']))

    axbig1.axhline(1. / settings['num_parties'], ls='--', lw=0.8, color='black', zorder=-10)
    x_list = [100.0 * x / settings['n'] for x in z_list]

    for system in systems:
        mean = np.array(systems_res[system]['mean'])
        std = np.array(systems_res[system]['std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        axbig1.plot(x_list, mean, color=color, ls='-', label=short, lw=1, zorder=10)
        axbig1.fill_between(x_list, mean - std, mean + std, color=color, lw=0, alpha=0.25, zorder=0)

    # axbig1.text(0.25, 0.35, r'$\varepsilon =$' + f'{settings["epsilon"]}')
    axbig1.set_title('a', loc='left', fontweight='bold', fontsize=title_font)
    axbig1.set_title('zealot susceptibility', fontsize=7)
    axbig1.set_xlabel('% of zealots')
    axbig1.set_ylabel('fraction of seats')
    axbig1.legend(loc=4)

    axbig1.set_xlim([0, x_list[-1]])
    axbig1.set_ylim([0.09, 1.005])

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################

    x_list = [100.0 * x / settings['n'] for x in z_list]
    for system in systems:
        mean = np.array(systems_res[system]['gall_mean'])
        std = np.array(systems_res[system]['gall_std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        axs[1, 0].plot(x_list, mean, color=color, ls='-', label=short, lw=1, zorder=10)
        axs[1, 0].fill_between(x_list, mean - std, mean + std, color=color, lw=0, alpha=0.25, zorder=0)

    axs[1, 0].set_title('b', loc='left', fontweight='bold', fontsize=title_font)
    axs[1, 0].set_xlabel('% of zealots')
    axs[1, 0].set_ylabel('Gallagher index')
    axs[1, 0].set_xlim([0, x_list[-1]])
    axs[1, 0].set_ylim([-0.01, 0.42])

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################

    for system in systems:
        mean = np.array(systems_res[system]['eff_mean'])
        std = np.array(systems_res[system]['eff_std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        axs[1, 1].plot(x_list, mean, color=color, ls='-', label=short, lw=1, zorder=10)
        axs[1, 1].fill_between(x_list, mean - std, mean + std, color=color, lw=0, alpha=0.25, zorder=0)

    axs[1, 1].set_title('c', loc='left', fontweight='bold', fontsize=title_font)
    axs[1, 1].set_xlabel('% of zealots')
    axs[1, 1].set_ylabel('eff. num. of parties')
    axs[1, 1].set_xlim([0, x_list[-1]])
    axs[1, 1].set_ylim([0.975, 9.02])
    axs[1, 1].set_yticks((1, 3, 5, 7, 9))
    axs[1, 1].set_yticklabels((1, 3, 5, 7, 9))

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################

    systems_res = defaultdict(lambda: defaultdict(list))

    args = parser.parse_args()
    setattr(args, 'n', 100000)
    setattr(args, 'mc_steps', 51)
    setattr(args, 'num_parties', 9)
    setattr(args, 'short_suffix', True)

    m_list = list(np.linspace(0, 1, 31))
    for i, m in enumerate(m_list):
        setattr(args, 'mass_media', m)
        cfg = Config(args, parser._option_string_actions)
        res, settings = read_data('_ind_house_otp' + cfg.suffix, input_dir='results/final3/')
        voting_distribution = convert_to_distributions(res['vote_fractions'])

        for system in systems:
            distribution = convert_to_distributions(res[system])
            systems_res[system]['data'].append(distribution['a'])
            systems_res[system]['mean'].append(np.mean(distribution['a']))
            systems_res[system]['std'].append(np.std(distribution['a']))
            indexes = calculate_indexes(voting_distribution, distribution, settings['sample_size'])
            systems_res[system]['gall_mean'].append(np.mean(indexes['Gallagher index']))
            systems_res[system]['gall_std'].append(np.std(indexes['Gallagher index']))
            systems_res[system]['loos_mean'].append(np.mean(indexes['Loosemore Hanby index']))
            systems_res[system]['loos_std'].append(np.std(indexes['Loosemore Hanby index']))
            systems_res[system]['eff_mean'].append(np.mean(indexes['Eff. No of Parties']))
            systems_res[system]['eff_std'].append(np.std(indexes['Eff. No of Parties']))

    axbig2.axhline(1. / settings['num_parties'], ls='--', lw=0.8, color='black', zorder=-10)
    axbig2.axvline(0, ls='--', lw=0.8, color='black', zorder=-10)
    x_list = np.array(m_list) - (1. / settings['num_parties'])

    for system in systems:
        mean = np.array(systems_res[system]['mean'])
        std = np.array(systems_res[system]['std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        axbig2.plot(x_list, mean, color=color, ls='-', label=short, lw=1, zorder=10)
        axbig2.fill_between(x_list, mean - std, mean + std, color=color, lw=0, alpha=0.25, zorder=0)

    # axbig2.text(0.12, 0.05, r'$\varepsilon =$' + f'{settings["epsilon"]}')
    axbig2.set_title('d', loc='left', fontweight='bold', fontsize=title_font)
    axbig2.set_title('media susceptibility', fontsize=7)
    axbig2.set_xlabel('media bias')
    axbig2.set_ylabel('fraction of seats')
    axbig2.legend(loc=4)

    axbig2.set_xlim([x_list[0], x_list[-1]])
    axbig2.set_ylim([-0.005, 1.005])

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################

    axs[3, 0].axvline(0, ls='--', lw=0.8, color='black', zorder=-10)
    x_list = np.array(m_list) - (1. / settings['num_parties'])
    for system in systems:
        mean = np.array(systems_res[system]['gall_mean'])
        std = np.array(systems_res[system]['gall_std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        axs[3, 0].plot(x_list, mean, color=color, ls='-', label=short, lw=1, zorder=10)
        axs[3, 0].fill_between(x_list, mean - std, mean + std, color=color, lw=0, alpha=0.25, zorder=0)

    axs[3, 0].set_title('e', loc='left', fontweight='bold', fontsize=title_font)
    axs[3, 0].set_xlabel('media bias')
    axs[3, 0].set_ylabel('Gallagher index')
    axs[3, 0].set_xlim([x_list[0], x_list[-1]])
    axs[3, 0].set_ylim([-0.01, 0.42])

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################

    axs[3, 1].axvline(0, ls='--', lw=0.8, color='black', zorder=-10)
    for system in systems:
        mean = np.array(systems_res[system]['eff_mean'])
        std = np.array(systems_res[system]['eff_std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        axs[3, 1].plot(x_list, mean, color=color, ls='-', label=short, lw=1, zorder=10)
        axs[3, 1].fill_between(x_list, mean - std, mean + std, color=color, lw=0, alpha=0.25, zorder=0)

    axs[3, 1].set_title('f', loc='left', fontweight='bold', fontsize=title_font)
    axs[3, 1].set_xlabel('media bias')
    axs[3, 1].set_ylabel('eff. num. of parties')
    axs[3, 1].set_xlim([x_list[0], x_list[-1]])
    axs[3, 1].set_ylim([0.975, 9.02])
    axs[3, 1].set_yticks((1, 3, 5, 7, 9))
    axs[3, 1].set_yticklabels((1, 3, 5, 7, 9))

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################

    plt.subplots_adjust(left=0.12, right=0.985, top=0.973, bottom=0.05, hspace=0.6, wspace=0.38)
    axbig1.set_position([0.2, 0.775, 0.7, 0.195])
    axbig2.set_position([0.2, 0.265, 0.7, 0.195])
    plt.savefig(f'plots/fig7.pdf')
    plt.close()


if __name__ == '__main__':
    main()

