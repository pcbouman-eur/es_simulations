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
from tools import convert_to_distributions, read_data
from plotting_scripts.plotting_tools import DefDict


names_dict = {
    'main_district_system': {
        'short': '15 dist. PR',
        'long': 'PR with 15 districts',
        'color': 'mediumorchid',
    },
    '6 districts': {
        'short': '6 dist. PR',
        'long': '',
        'color': 'deepskyblue',
    },
    'countrywide_system': {
        'short': '1 dist. PR*',
        'long': '',
        'color': 'mediumseagreen',
    },
    '15 districts FPTP': {
        'short': '15 dist. PV',
        'long': '',
        'color': 'sandybrown',
    },
    '6 districts FPTP': {
        'short': '6 dist. PV',
        'long': '',
        'color': 'orangered',
    },
}


def main(arguments=None, input_dir=None, num=None, big=False, num2=None):
    systems_res = defaultdict(DefDict)
    systems = ['main_district_system', '15 districts FPTP', '6 districts FPTP', '6 districts', 'countrywide_system']

    m_list = list(np.linspace(0, 1, 31))
    for i, m in enumerate(m_list):
        setattr(arguments, 'mass_media', m)
        cfg = Config(arguments, parser._option_string_actions)
        if 'final1' not in input_dir:
            res, settings = read_data('_il_knesset_m' + cfg.suffix, input_dir=input_dir)
        else:
            res, settings = read_data('_il_knesset' + cfg.suffix, input_dir=input_dir)

        for system in systems:
            distribution = convert_to_distributions(res[system])
            systems_res[system]['data'].append(distribution['a'])
            systems_res[system]['mean'].append(np.mean(distribution['a']))
            systems_res[system]['std'].append(np.std(distribution['a']))

    if not big:
        plt.figure(figsize=(3.5, 2.7))
    else:
        plt.figure(figsize=(6, 4.5))
    plt.axhline(1./settings['num_parties'], ls='--', lw=0.9, color='black')
    plt.axvline(0, ls='--', lw=0.9, color='black')
    x_list = np.array(m_list) - (1./settings['num_parties'])

    for system in systems:
        mean = np.array(systems_res[system]['mean'])
        std = np.array(systems_res[system]['std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        plt.plot(x_list, mean, color=color, ls='-', label=short, lw=2, zorder=10)
        plt.fill_between(x_list, mean-std, mean+std, color=color, lw=0, alpha=0.25, zorder=0)

    if big:
        plt.title(r'media susceptibility                   $\varepsilon =$'+f'{settings["epsilon"]}', loc='right')
    else:
        plt.title('media susceptibility')
        plt.text(0.55, 0.35, r'$\varepsilon =$' + f'{settings["epsilon"]}')
    plt.title(num, loc='left', fontweight='bold')
    plt.xlabel('media bias')
    plt.ylabel('fraction of seats')
    if big:
        plt.legend(loc=5)
    plt.tight_layout()

    plt.xlim([x_list[0], x_list[-1]])
    plt.ylim([-0.005, 1.005])

    plt.savefig(f'plots/il_knesset_m_sus_eps{settings["epsilon"]}.pdf')
    plt.close()

    ########################################################################################
    # marginal susceptibility
    plt.figure(figsize=(3.5, 2.7))
    plt.axvline(0, ls='--', lw=0.9, color='black')
    for system in systems:
        mean = np.array(systems_res[system]['mean'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        plt.plot(x_list[:4], ((mean - 1./settings['num_parties']) / x_list)[:4], color=color, ls='-', label=short, lw=2)
        plt.plot(x_list[4:], ((mean - 1./settings['num_parties']) / x_list)[4:], color=color, ls='-', lw=2)
    plt.xlim([x_list[0], x_list[-1]])
    plt.ylim([0.9, 8])
    plt.title('marginal susceptibility')
    if num2 == 'f':
        plt.text(0.1, 6.5, r'$\varepsilon =$' + f'{settings["epsilon"]}')
    else:
        plt.text(0.55, 6.5, r'$\varepsilon =$' + f'{settings["epsilon"]}')
    plt.title(num2, loc='left', fontweight='bold')
    plt.xlabel('media bias')
    plt.ylabel('fraction of seats')
    if num2 == 'f':
        plt.legend(loc=1, fontsize=9)

    plt.tight_layout()
    plt.savefig(f'plots/il_knesset_m_sus_marginal_eps{settings["epsilon"]}.pdf')
    plt.close()


if __name__ == '__main__':
    os.chdir(parentdir)
    args = parser.parse_args()
    setattr(args, 'n', 9000)
    setattr(args, 'mc_steps', 50)
    setattr(args, 'num_parties', 8)
    setattr(args, 'short_suffix', True)

    main(arguments=args, input_dir='results/final1/', num='c', num2='f')  # eps=0.006

    setattr(args, 'mc_steps', 50)
    main(arguments=args, input_dir='results/final2/', num='b', num2='e')  # eps=0.01

    setattr(args, 'mc_steps', 51)
    main(arguments=args, input_dir='results/final3/', num='a', num2='d', big=True)  # eps=0.02


