import os
import sys
import inspect
import numpy as np
from matplotlib import pyplot as plt
from collections import defaultdict
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# path hack for imports to work when running this script from any location,
# without the hack one has to manually edit PYTHONPATH every time
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from configuration.parser import parser
from configuration.config import Config
from tools import convert_to_distributions, read_data, calculate_indexes
from plotting_scripts.plotting_tools import names_dict


def main(arguments=None, input_dir=None):
    systems_res = defaultdict(lambda: defaultdict(list))
    systems = ['100 districts FPTP', 'main_district_system', '100 districts Webster', 'countrywide_system']

    m_list = list(np.linspace(0, 1, 31))
    for i, m in enumerate(m_list):
        setattr(arguments, 'mass_media', m)
        cfg = Config(arguments, parser._option_string_actions)
        res, settings = read_data('_basic_m' + cfg.suffix, input_dir=input_dir)
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

    x_list = np.array(m_list)-1./3

    ############################################################
    plt.figure(figsize=(3.5, 2.7))
    plt.axvline(0, ls='--', lw=0.9, color='black')
    for system in systems:
        mean = np.array(systems_res[system]['gall_mean'])
        std = np.array(systems_res[system]['gall_std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        plt.plot(x_list, mean, color=color, ls='-', label=short, lw=2)
        plt.fill_between(x_list, mean-std, mean+std, color=color, lw=0, alpha=0.45)

    plt.title('disproportionality')
    plt.title('c', loc='left', fontweight='bold')
    plt.xlabel('media bias')
    plt.ylabel('Gallagher index')
    plt.legend(loc=2, fontsize=9)
    plt.xlim([-1/3, 2/3])
    plt.ylim([-0.01, 0.42])
    plt.tight_layout()
    plt.savefig(f'plots/m_sus_gall.pdf')
    plt.close()

    ############################################################
    plt.figure(figsize=(3.5, 2.7))
    plt.axvline(0, ls='--', lw=0.9, color='black')
    for system in systems:
        mean = np.array(systems_res[system]['loos_mean'])
        std = np.array(systems_res[system]['loos_std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        plt.plot(x_list, mean, color=color, ls='-', label=short, lw=2)
        plt.fill_between(x_list, mean - std, mean + std, color=color, lw=0, alpha=0.45)

    plt.title('disproportionality')
    plt.title('d', loc='left', fontweight='bold')
    plt.xlabel('media bias')
    plt.ylabel('Loosemore-Hanby index')
    plt.legend(loc=2, fontsize=9)
    plt.xlim([-1/3, 2/3])
    plt.ylim([-0.01, 0.42])
    plt.tight_layout()
    plt.savefig(f'plots/m_sus_loos.pdf')
    plt.close()

    ############################################################
    plt.figure(figsize=(3.5, 2.7))
    plt.axvline(0, ls='--', lw=0.9, color='black')
    for system in systems:
        mean = np.array(systems_res[system]['eff_mean'])
        std = np.array(systems_res[system]['eff_std'])
        short = names_dict[system]['short']
        color = names_dict[system]['color']
        plt.plot(x_list, mean, color=color, ls='-', label=short, lw=2)
        plt.fill_between(x_list, mean - std, mean + std, color=color, lw=0, alpha=0.45)

    plt.title('fragmentation')
    plt.title('e', loc='left', fontweight='bold')
    plt.xlabel('media bias')
    plt.ylabel('effective num. of parties')
    plt.legend(loc=1, fontsize=9)
    plt.xlim([-1/3, 2/3])
    plt.ylim([0.975, 3.02])
    plt.tight_layout()
    plt.savefig(f'plots/m_sus_eff.pdf')
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

    main(arguments=args, input_dir='results/final1/')

