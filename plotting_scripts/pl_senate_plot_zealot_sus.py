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


def main(arguments=None, input_dir=None, num=None, big=False, num2=None):
    systems_res = defaultdict(DefDict)
    systems = ['main_district_system', '40 old districts', '40 old districts FPTP', '16 districts', '16 districts FPTP', 'countrywide_system']

    z_list = list(range(0, 800, 27))
    for i, z in enumerate(z_list):
        setattr(arguments, 'n_zealots', z)
        cfg = Config(arguments, parser._option_string_actions)
        if 'final3' in input_dir:
            res, settings = read_data('_pl_senate_z' + cfg.suffix, input_dir=input_dir)
        else:
            res, settings = read_data('_pl_senate' + cfg.suffix, input_dir=input_dir)

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
    x_list = [100.0 * x / settings['n'] for x in z_list]

    for system in systems:
        mean = np.array(systems_res[system]['mean'])
        std = np.array(systems_res[system]['std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        plt.plot(x_list, mean, color=color, ls='-', label=short, lw=2, zorder=10)
        plt.fill_between(x_list, mean-std, mean+std, color=color, lw=0, alpha=0.25, zorder=0)

    if big:
        plt.title(r'zealot susceptibility                  $\varepsilon =$'+f'{settings["epsilon"]}', loc='right')
    else:
        plt.title('zealot susceptibility')
        plt.text(1, 0.4, r'$\varepsilon =$' + f'{settings["epsilon"]}')
    plt.title(num, loc='left', fontweight='bold')
    plt.xlabel('% of zealots')
    plt.ylabel('fraction of seats')
    if big:
        plt.legend(loc=5)
    plt.tight_layout()

    plt.xlim([0, x_list[-1]])
    plt.ylim([0.3, 1.005])

    plt.savefig(f'plots/pl_senate_z_sus_eps{settings["epsilon"]}.pdf')
    plt.close()

    ########################################################################################
    # marginal susceptibility
    plt.figure(figsize=(3.5, 2.7))
    for system in systems:
        mean = np.array(systems_res[system]['mean'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        plt.plot(x_list[1:], (mean[1:] - mean[0]) / np.array(z_list[1:]), color=color, ls='-', label=short, lw=2)
    plt.xlim([0, x_list[-1]])
    plt.ylim([0., 0.015])
    plt.title('marginal susceptibility')
    if num2 == 'f':
        plt.text(0.15, 0.013, r'$\varepsilon =$' + f'{settings["epsilon"]}')
    else:
        plt.text(1, 0.012, r'$\varepsilon =$' + f'{settings["epsilon"]}')
    ax = plt.gca()
    ax.set_yticks((0, 0.005, 0.010, 0.015))
    plt.title(num2, loc='left', fontweight='bold')
    plt.xlabel('% of zealots')
    plt.ylabel('fraction of seats')
    if num2 == 'f':
        plt.legend(loc=1, fontsize=9)

    plt.tight_layout()
    plt.savefig(f'plots/pl_senate_z_sus_marginal_eps{settings["epsilon"]}.pdf')
    plt.close()


if __name__ == '__main__':
    os.chdir(parentdir)
    args = parser.parse_args()
    setattr(args, 'n', 50000)
    setattr(args, 'mc_steps', 50)  # the name of the file has a wrong value
    setattr(args, 'num_parties', 3)
    setattr(args, 'short_suffix', True)

    main(arguments=args, input_dir='results/final1/', num='c', num2='f')  # eps=0.0005

    setattr(args, 'mc_steps', 600)
    main(arguments=args, input_dir='results/final2/', num='b', num2='e')  # eps=0.001

    setattr(args, 'mc_steps', 600)
    main(arguments=args, input_dir='results/final3/', num='a', num2='d', big=True)  # eps=0.002


