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
from plotting_scripts.plotting_tools import names_dict, DefDict


def main(system, arguments=None):
    plt.figure(figsize=(5, 3.5))
    plt.axhline(1. / 3, ls='--', lw=0.9, color='black')
    plt.axvline(0, ls='--', lw=0.9, color='black')

    m_list = list(np.linspace(0, 1, 31))
    x_list = np.array(m_list)-1./3

    systems_res = defaultdict(DefDict)
    for i, m in enumerate(m_list):
        setattr(arguments, 'mass_media', m)
        cfg = Config(arguments, parser._option_string_actions)
        res, settings = read_data('_basic_m' + cfg.suffix, input_dir='results/final1/')
        distribution = convert_to_distributions(res[system])
        systems_res[system]['mean'].append(np.mean(distribution['a']))
        systems_res[system]['std'].append(np.std(distribution['a']))
    mean = np.array(systems_res[system]['mean'])
    color = names_dict[system]['color']
    plt.plot(x_list, mean, color=color, ls='-', lw=2.2, label='standard')

    systems_res = defaultdict(DefDict)
    for i, m in enumerate(m_list):
        setattr(arguments, 'mass_media', m)
        cfg = Config(arguments, parser._option_string_actions)
        res, settings = read_data('_basic_m' + cfg.suffix, input_dir='results/final3/')
        distribution = convert_to_distributions(res[system])
        systems_res[system]['mean'].append(np.mean(distribution['a']))
        systems_res[system]['std'].append(np.std(distribution['a']))
    mean = np.array(systems_res[system]['mean'])
    plt.plot(x_list, mean, color='darkcyan', ls='--', lw=2, label=r'$k=50$')

    setattr(arguments, 'mc_steps', 49)

    systems_res = defaultdict(DefDict)
    for i, m in enumerate(m_list):
        setattr(arguments, 'mass_media', m)
        cfg = Config(arguments, parser._option_string_actions)
        res, settings = read_data('_basic_m' + cfg.suffix, input_dir='results/final3/')
        distribution = convert_to_distributions(res[system])
        systems_res[system]['mean'].append(np.mean(distribution['a']))
        systems_res[system]['std'].append(np.std(distribution['a']))
    mean = np.array(systems_res[system]['mean'])
    plt.plot(x_list, mean, color='mediumorchid', ls='-.', lw=2, label=r'$\varepsilon=0.01$')

    setattr(arguments, 'mc_steps', 51)

    systems_res = defaultdict(DefDict)
    for i, m in enumerate(m_list):
        setattr(arguments, 'mass_media', m)
        cfg = Config(arguments, parser._option_string_actions)
        res, settings = read_data('_basic_m' + cfg.suffix, input_dir='results/final3/')
        distribution = convert_to_distributions(res[system])
        systems_res[system]['mean'].append(np.mean(distribution['a']))
        systems_res[system]['std'].append(np.std(distribution['a']))
    mean = np.array(systems_res[system]['mean'])
    plt.plot(x_list, mean, color='darkorange', ls=':', lw=2, label=r'$r=0.007$')

    setattr(arguments, 'mc_steps', 52)
    setattr(arguments, 'num_parties', 6)

    systems_res = defaultdict(DefDict)
    for i, m in enumerate(m_list):
        setattr(arguments, 'mass_media', m)
        cfg = Config(arguments, parser._option_string_actions)
        res, settings = read_data('_basic_m' + cfg.suffix, input_dir='results/final3/')
        distribution = convert_to_distributions(res[system])
        systems_res[system]['mean'].append(np.mean(distribution['a']))
        systems_res[system]['std'].append(np.std(distribution['a']))
    mean = np.array(systems_res[system]['mean'])
    plt.plot(np.array(m_list)-1./6, mean, color='goldenrod', ls=(0, (3, 1, 1, 1, 1, 1)), lw=2, label='6 parties')

    plt.title('PR')
    plt.title('a', loc='left', fontweight='bold')
    plt.xlabel('media bias')
    plt.ylabel('fraction of seats')
    plt.legend(loc=4)

    plt.xlim([-1/3, 2/3])
    plt.ylim([0, 1])

    plt.tight_layout()
    plt.savefig(f'plots/m_sus_pr.pdf')
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

    main('main_district_system', arguments=args)

