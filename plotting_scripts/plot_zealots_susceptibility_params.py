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

    z_list = list(range(0, 400, 13))
    for i, z in enumerate(z_list):
        setattr(arguments, 'n_zealots', z)
        cfg = Config(arguments, parser._option_string_actions)
        res, settings = read_data('_basic_z' + cfg.suffix, input_dir=input_dir)
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

    plt.figure(figsize=(2.5, 2.2))
    if title == '6 parties':
        plt.axhline(1./6, ls='--', lw=0.9, color='black')
    else:
        plt.axhline(1. / 3, ls='--', lw=0.9, color='black')
    x_list = [100.0 * x / 10000 for x in z_list]

    for system in systems:
        mean = np.array(systems_res[system]['mean'])
        std = np.array(systems_res[system]['std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        plt.plot(x_list, mean, color=color, ls='-', label=short)
        plt.fill_between(x_list, mean-std, mean+std, color=color, lw=0, alpha=0.4)

    plt.title(title)
    plt.title(num, loc='left', fontweight='bold')
    plt.xlabel('% of zealots')
    plt.ylabel('fraction of seats')
    plt.legend(loc=4)

    plt.xlim([0, z_list[-1]/100.])
    plt.ylim([0.13, 1.005])

    plt.subplots_adjust(top=0.87, bottom=0.22, left=0.21, right=0.99)
    plt.savefig(f'plots/z_sus_{save}.pdf')
    plt.close()


if __name__ == '__main__':
    os.chdir(parentdir)
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

    main(arguments=args, input_dir='results/final3/', title=r'$k=50$', save='k', num='h')
    setattr(args, 'mc_steps', 999)
    main(arguments=args, input_dir='results/final3/', title=r'$\varepsilon=0.01$', save='eps', num='i')
    setattr(args, 'mc_steps', 1001)
    main(arguments=args, input_dir='results/final3/', title=r'$r=0.007$', save='r', num='j')
    setattr(args, 'mc_steps', 1002)
    setattr(args, 'num_parties', 6)
    main(arguments=args, input_dir='results/final3/', title='6 parties', save='parties', num='k')
