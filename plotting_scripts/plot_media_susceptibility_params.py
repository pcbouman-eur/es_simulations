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
from plotting_scripts.plotting_tools import names_dict, DefDict


def main(arguments=None, input_dir=None, title=None, save=None, num=None):
    systems_res = defaultdict(DefDict)
    systems = ['100 districts FPTP', 'main_district_system', '100 districts Webster', 'countrywide_system']

    m_list = list(np.linspace(0, 1, 31))
    for i, m in enumerate(m_list):
        setattr(arguments, 'mass_media', m)
        cfg = Config(arguments, parser._option_string_actions)
        res, settings = read_data('_basic_m' + cfg.suffix, input_dir=input_dir)
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

    plt.figure(figsize=(2.8, 2.4))
    if title == '6 parties':
        plt.axhline(1./6, ls='--', lw=0.9, color='black')
    else:
        plt.axhline(1. / 3, ls='--', lw=0.9, color='black')
    plt.axvline(0, ls='--', lw=0.9, color='black')

    for system in systems:
        mean = np.array(systems_res[system]['mean'])
        std = np.array(systems_res[system]['std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        if title == '6 parties':
            x_list = np.array(m_list) - 1. / 6
        else:
            x_list = np.array(m_list) - 1. / 3
        plt.plot(x_list, mean, color=color, ls='-', label=short)
        plt.fill_between(x_list, mean-std, mean+std, color=color, lw=0, alpha=0.4)

    plt.title(title)
    plt.title(num, loc='left', fontweight='bold')
    plt.xlabel('media bias')
    plt.ylabel('fraction of seats')
    plt.legend(loc=4, fontsize=9)

    if title == '6 parties':
        plt.xlim([-1 / 6, 5 / 6])
    else:
        plt.xlim([-1 / 3, 2 / 3])
    plt.ylim([-0.005, 1.005])

    plt.tight_layout()
    plt.savefig(f'plots/m_sus_{save}.pdf')
    plt.close()


if __name__ == '__main__':
    os.chdir(parentdir)
    args = parser.parse_args()
    setattr(args, 'n', 10000)
    setattr(args, 'q', 100)
    setattr(args, 'sample_size', 1000)
    setattr(args, 'mc_steps', 50)
    setattr(args, 'therm_time', 10000000)
    setattr(args, 'seats', [5])
    setattr(args, 'ratio', 0.002)
    setattr(args, 'avg_deg', 12.0)
    setattr(args, 'epsilon', 0.005)
    setattr(args, 'num_parties', 3)
    setattr(args, 'short_suffix', True)

    main(arguments=args, input_dir='results/final3/', title=r'$k=50$', save='k', num='j')
    setattr(args, 'mc_steps', 49)
    main(arguments=args, input_dir='results/final3/', title=r'$\varepsilon=0.01$', save='eps', num='k')
    setattr(args, 'mc_steps', 51)
    main(arguments=args, input_dir='results/final3/', title=r'$r=0.007$', save='r', num='l')
    setattr(args, 'mc_steps', 52)
    setattr(args, 'num_parties', 6)
    main(arguments=args, input_dir='results/final3/', title='6 parties', save='parties', num='m')
