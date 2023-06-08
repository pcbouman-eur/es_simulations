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
from tools import convert_to_distributions, read_data, calculate_indexes


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


def main(arguments=None, input_dir=None):
    systems_res = defaultdict(lambda: defaultdict(list))
    systems = ['main_district_system', '132 districts', '132 districts FPTP', '36 districts', 'countrywide_system']

    m_list = list(np.linspace(0, 1, 31))
    for i, m in enumerate(m_list):
        setattr(arguments, 'mass_media', m)
        cfg = Config(arguments, parser._option_string_actions)
        res, settings = read_data('_ind_house_otp' + cfg.suffix, input_dir=input_dir)
        voting_distribution = convert_to_distributions(res['vote_fractions'])

        for system in systems:
            distribution = convert_to_distributions(res[system])
            indexes = calculate_indexes(voting_distribution, distribution, settings['sample_size'])
            systems_res[system]['gall_mean'].append(np.mean(indexes['Gallagher index']))
            systems_res[system]['gall_std'].append(np.std(indexes['Gallagher index']))
            systems_res[system]['loos_mean'].append(np.mean(indexes['Loosemore Hanby index']))
            systems_res[system]['loos_std'].append(np.std(indexes['Loosemore Hanby index']))
            systems_res[system]['eff_mean'].append(np.mean(indexes['Eff. No of Parties']))
            systems_res[system]['eff_std'].append(np.std(indexes['Eff. No of Parties']))

    plt.figure(figsize=(3.5, 2.7))
    plt.axvline(0, ls='--', lw=0.9, color='black')
    x_list = np.array(m_list) - (1./settings['num_parties'])
    for system in systems:
        mean = np.array(systems_res[system]['gall_mean'])
        std = np.array(systems_res[system]['gall_std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        plt.plot(x_list, mean, color=color, ls='-', label=short, lw=2, zorder=10)
        plt.fill_between(x_list, mean - std, mean + std, color=color, lw=0, alpha=0.25, zorder=0)

    plt.title('disproportionality')
    plt.title('g', loc='left', fontweight='bold')
    plt.xlabel('media bias')
    plt.ylabel('Gallagher index')
    plt.text(0.55, 0.45, r'$\varepsilon =$'+f'{settings["epsilon"]}')
    plt.xlim([x_list[0], x_list[-1]])
    plt.ylim([-0.01, 0.55])
    plt.tight_layout()
    plt.savefig(f'plots/ind_house_otp_m_sus_gall.pdf')
    plt.close()

    ############################################################
    plt.figure(figsize=(3.5, 2.7))
    plt.axvline(0, ls='--', lw=0.9, color='black')

    for system in systems:
        mean = np.array(systems_res[system]['loos_mean'])
        std = np.array(systems_res[system]['loos_std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        plt.plot(x_list, mean, color=color, ls='-', label=short, lw=2, zorder=10)
        plt.fill_between(x_list, mean - std, mean + std, color=color, lw=0, alpha=0.25, zorder=0)

    plt.title('disproportionality')
    plt.title('h', loc='left', fontweight='bold')
    plt.xlabel('media bias')
    plt.ylabel('Loosemore-Hanby index')
    plt.text(0.55, 0.45, r'$\varepsilon =$'+f'{settings["epsilon"]}')
    plt.xlim([x_list[0], x_list[-1]])
    plt.ylim([-0.01, 0.55])
    plt.tight_layout()
    plt.savefig(f'plots/ind_house_otp_m_sus_loos.pdf')
    plt.close()

    ############################################################
    plt.figure(figsize=(3.5, 2.7))
    plt.axvline(0, ls='--', lw=0.9, color='black')
    for system in systems:
        mean = np.array(systems_res[system]['eff_mean'])
        std = np.array(systems_res[system]['eff_std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        plt.plot(x_list, mean, color=color, ls='-', label=short, lw=2, zorder=10)
        plt.fill_between(x_list, mean - std, mean + std, color=color, lw=0, alpha=0.25, zorder=0)

    plt.title('fragmentation')
    plt.title('i', loc='left', fontweight='bold')
    plt.xlabel('media bias')
    plt.ylabel('effective num. of parties')
    plt.text(-0.075, 4.1, r'$\varepsilon =$'+f'{settings["epsilon"]}', rotation=90)
    plt.legend(loc=1, fontsize=9)
    plt.xlim([x_list[0], x_list[-1]])
    plt.ylim([0.975, 9.])
    plt.tight_layout()
    plt.savefig(f'plots/ind_house_otp_m_sus_eff.pdf')
    plt.close()


if __name__ == '__main__':
    os.chdir(parentdir)
    args = parser.parse_args()
    setattr(args, 'n', 100000)
    setattr(args, 'mc_steps', 50)
    setattr(args, 'num_parties', 9)
    setattr(args, 'short_suffix', True)

    # main(arguments=args, input_dir='results/final1/')  # eps=0.0001
    #
    # setattr(args, 'mc_steps', 49)
    # main(arguments=args, input_dir='results/final2/')  # eps=0.0007

    setattr(args, 'mc_steps', 51)
    main(arguments=args, input_dir='results/final3/')  # eps=0.002


