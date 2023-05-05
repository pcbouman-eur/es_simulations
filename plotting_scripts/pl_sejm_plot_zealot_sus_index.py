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
        'short': 'real ES',
        'long': 'PR with 41 districts',
        'color': 'mediumorchid',
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
    '41 districts FPTP': {
        'short': '41 dist. PV',
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
    systems = ['main_district_system', '41 districts FPTP', '16 districts', '16 districts FPTP', 'countrywide_system']

    z_list = list(range(0, 400, 13))
    for i, z in enumerate(z_list):
        setattr(arguments, 'n_zealots', z)
        cfg = Config(arguments, parser._option_string_actions)
        res, settings = read_data('_pl_sejm' + cfg.suffix, input_dir=input_dir)
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
    x_list = [100.0 * x / 10000 for x in z_list]
    for system in systems:
        mean = np.array(systems_res[system]['gall_mean'])
        std = np.array(systems_res[system]['gall_std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        plt.plot(x_list, mean, color=color, ls='-', label=short, lw=2)
        plt.fill_between(x_list, mean - std, mean + std, color=color, lw=0, alpha=0.45)

    plt.title('disproportionality')
    plt.title('g', loc='left', fontweight='bold')
    plt.xlabel('% of zealots')
    plt.ylabel('Gallagher index')
    plt.text(0.05, 0.4, r'$\varepsilon =$'+f'{settings["epsilon"]}')
    # plt.legend(loc=1)
    plt.xlim([0, 100. * z_list[-1] / cfg.n])
    plt.ylim([-0.01, 0.46])
    plt.tight_layout()
    plt.savefig(f'plots/pl_sejm_z_sus_gall.pdf')
    plt.close()

    ############################################################
    plt.figure(figsize=(3.5, 2.7))
    x_list = [100.0 * x / 10000 for x in z_list]
    for system in systems:
        mean = np.array(systems_res[system]['loos_mean'])
        std = np.array(systems_res[system]['loos_std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        plt.plot(x_list, mean, color=color, ls='-', label=short, lw=2)
        plt.fill_between(x_list, mean - std, mean + std, color=color, lw=0, alpha=0.45)

    plt.title('disproportionality')
    plt.title('h', loc='left', fontweight='bold')
    plt.xlabel('% of zealots')
    plt.ylabel('Loosemore-Hanby index')
    plt.text(0.05, 0.4, r'$\varepsilon =$'+f'{settings["epsilon"]}')
    # plt.legend(loc=1)
    plt.xlim([0, 100. * z_list[-1] / cfg.n])
    plt.ylim([-0.01, 0.46])
    plt.tight_layout()
    plt.savefig(f'plots/pl_sejm_z_sus_loos.pdf')
    plt.close()

    ############################################################
    plt.figure(figsize=(3.5, 2.7))
    x_list = [100.0 * x / 10000 for x in z_list]
    for system in systems:
        mean = np.array(systems_res[system]['eff_mean'])
        std = np.array(systems_res[system]['eff_std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        plt.plot(x_list, mean, color=color, ls='-', label=short, lw=2)
        plt.fill_between(x_list, mean - std, mean + std, color=color, lw=0, alpha=0.45)

    plt.title('fragmentation')
    plt.title('i', loc='left', fontweight='bold')
    plt.xlabel('% of zealots')
    plt.ylabel('effective num. of parties')
    plt.text(0.7, 4.5, r'$\varepsilon =$'+f'{settings["epsilon"]}')
    # plt.legend(loc=1, fontsize=9)
    plt.xlim([0, 100. * z_list[-1] / cfg.n])
    plt.ylim([0.975, 5.02])
    plt.tight_layout()
    plt.savefig(f'plots/pl_sejm_z_sus_eff.pdf')
    plt.close()


if __name__ == '__main__':
    os.chdir(parentdir)
    args = parser.parse_args()
    setattr(args, 'n', 41000)
    setattr(args, 'mc_steps', 50)
    setattr(args, 'num_parties', 5)
    setattr(args, 'short_suffix', True)

    # main(arguments=args, input_dir='results/final1/')  # eps=0.001

    setattr(args, 'mc_steps', 700)
    main(arguments=args, input_dir='results/final2/')  # eps=0.002

    # setattr(args, 'mc_steps', 700)
    # main(arguments=args, input_dir='results/final3/')   # eps=0.005


