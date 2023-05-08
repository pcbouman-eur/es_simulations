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
        'short': '100 dist. PV*',
        'long': 'FPTP 100 districts',
        'color': 'mediumorchid',
    },
    '40 old districts': {
        'short': '40 dist. PR',
        'long': '',
        'color': '#d3c655',  # E1357A
    },
    '16 districts': {
        'short': '16 dist. PR',
        'long': '',
        'color': 'deepskyblue',
    },
    'countrywide_system': {
        'short': '1 dist. PR',
        'long': '',
        'color': 'mediumseagreen',
    },
    '40 old districts FPTP': {
        'short': '40 dist. PV',
        'long': '',
        'color': 'sandybrown',
    },
    '16 districts FPTP': {
        'short': '16 dist. PV',
        'long': '',
        'color': 'orangered',
    },
}


def main(arguments=None, input_dir=None):
    systems_res = defaultdict(lambda: defaultdict(list))
    systems = ['main_district_system', '40 old districts', '40 old districts FPTP', '16 districts', '16 districts FPTP', 'countrywide_system']

    z_list = list(range(0, 800, 27))
    for i, z in enumerate(z_list):
        setattr(arguments, 'n_zealots', z)
        cfg = Config(arguments, parser._option_string_actions)
        if 'final3' in input_dir:
            res, settings = read_data('_pl_senate_z' + cfg.suffix, input_dir=input_dir)
        else:
            res, settings = read_data('_pl_senate' + cfg.suffix, input_dir=input_dir)
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
    x_list = [100.0 * x / settings['n'] for x in z_list]
    for system in systems:
        mean = np.array(systems_res[system]['gall_mean'])
        std = np.array(systems_res[system]['gall_std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        plt.plot(x_list, mean, color=color, ls='-', label=short, lw=2, zorder=10)
        plt.fill_between(x_list, mean - std, mean + std, color=color, lw=0, alpha=0.25, zorder=0)

    plt.title('disproportionality')
    plt.title('g', loc='left', fontweight='bold')
    plt.xlabel('% of zealots')
    plt.ylabel('Gallagher index')
    plt.text(1.0, 0.37, r'$\varepsilon =$'+f'{settings["epsilon"]}')
    # plt.legend(loc=1)
    plt.xlim([0, x_list[-1]])
    plt.ylim([-0.01, 0.46])
    plt.tight_layout()
    plt.savefig(f'plots/pl_senate_z_sus_gall.pdf')
    plt.close()

    ############################################################
    plt.figure(figsize=(3.5, 2.7))
    for system in systems:
        mean = np.array(systems_res[system]['loos_mean'])
        std = np.array(systems_res[system]['loos_std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        plt.plot(x_list, mean, color=color, ls='-', label=short, lw=2, zorder=10)
        plt.fill_between(x_list, mean - std, mean + std, color=color, lw=0, alpha=0.25, zorder=0)

    plt.title('disproportionality')
    plt.title('h', loc='left', fontweight='bold')
    plt.xlabel('% of zealots')
    plt.ylabel('Loosemore-Hanby index')
    plt.text(1.0, 0.37, r'$\varepsilon =$'+f'{settings["epsilon"]}')
    # plt.legend(loc=1)
    plt.xlim([0, x_list[-1]])
    plt.ylim([-0.01, 0.46])
    plt.tight_layout()
    plt.savefig(f'plots/pl_senate_z_sus_loos.pdf')
    plt.close()

    ############################################################
    plt.figure(figsize=(3.5, 2.7))
    for system in systems:
        mean = np.array(systems_res[system]['eff_mean'])
        std = np.array(systems_res[system]['eff_std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        plt.plot(x_list, mean, color=color, ls='-', label=short, lw=2, zorder=10)
        plt.fill_between(x_list, mean - std, mean + std, color=color, lw=0, alpha=0.25, zorder=0)

    plt.title('fragmentation')
    plt.title('i', loc='left', fontweight='bold')
    plt.xlabel('% of zealots')
    plt.ylabel('effective num. of parties')
    plt.text(0.32, 2.6, r'$\varepsilon =$'+f'{settings["epsilon"]}')
    plt.legend(loc=1, fontsize=9)
    plt.xlim([0, x_list[-1]])
    plt.ylim([0.975, 3.02])
    plt.tight_layout()
    plt.savefig(f'plots/pl_senate_z_sus_eff.pdf')
    plt.close()


if __name__ == '__main__':
    os.chdir(parentdir)
    args = parser.parse_args()
    setattr(args, 'n', 50000)
    setattr(args, 'mc_steps', 50)  # the name of the file has a wrong value
    setattr(args, 'num_parties', 3)
    setattr(args, 'short_suffix', True)

    # main(arguments=args, input_dir='results/final1/')  # eps=0.0005

    # setattr(args, 'mc_steps', 600)
    # main(arguments=args, input_dir='results/final2/')  # eps=0.001

    setattr(args, 'mc_steps', 600)
    main(arguments=args, input_dir='results/final3/')  # eps=0.002


