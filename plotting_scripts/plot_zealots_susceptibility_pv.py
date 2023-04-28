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


def main(system, arguments=None):
    plt.figure(figsize=(3.5, 2.7))
    plt.axhline(1. / 3, ls='--', lw=0.9, color='black')

    z_list = list(range(0, 400, 13))
    x_list = [100.0 * x / 10000 for x in z_list]

    systems_res = defaultdict(DefDict)
    for i, z in enumerate(z_list):
        setattr(arguments, 'n_zealots', z)
        cfg = Config(arguments, parser._option_string_actions)
        res, settings = read_data('_basic_z' + cfg.suffix, input_dir='results/final1/')
        distribution = convert_to_distributions(res[system])
        systems_res[system]['mean'].append(np.mean(distribution['a']))
        systems_res[system]['std'].append(np.std(distribution['a']))
    mean = np.array(systems_res[system]['mean'])
    std = np.array(systems_res[system]['std'])
    color = names_dict[system]['color']
    plt.plot(x_list, mean, color=color, ls='-', lw=2.2, label='standard')
    # plt.scatter(x_list, mean, color=color, label='standard', facecolor='none', marker='o', s=50)
    # plt.fill_between(x_list, mean-std, mean+std, color=color, lw=0, alpha=0.4)

    systems_res = defaultdict(DefDict)
    for i, z in enumerate(z_list):
        setattr(arguments, 'n_zealots', z)
        cfg = Config(arguments, parser._option_string_actions)
        res, settings = read_data('_basic_z' + cfg.suffix, input_dir='results/final3/')
        distribution = convert_to_distributions(res[system])
        systems_res[system]['mean'].append(np.mean(distribution['a']))
        systems_res[system]['std'].append(np.std(distribution['a']))
    mean = np.array(systems_res[system]['mean'])
    std = np.array(systems_res[system]['std'])
    plt.plot(x_list, mean, color='darkcyan', ls='--', lw=2, label=r'$k=50$')
    # plt.scatter(x_list, mean, color='mediumorchid', label=r'$k=50$', marker='x')
    # plt.fill_between(x_list, mean-std, mean+std, color='mediumorchid', lw=0, alpha=0.4)

    setattr(arguments, 'mc_steps', 999)

    systems_res = defaultdict(DefDict)
    for i, z in enumerate(z_list):
        setattr(arguments, 'n_zealots', z)
        cfg = Config(arguments, parser._option_string_actions)
        res, settings = read_data('_basic_z' + cfg.suffix, input_dir='results/final3/')
        distribution = convert_to_distributions(res[system])
        systems_res[system]['mean'].append(np.mean(distribution['a']))
        systems_res[system]['std'].append(np.std(distribution['a']))
    mean = np.array(systems_res[system]['mean'])
    std = np.array(systems_res[system]['std'])
    plt.plot(x_list, mean, color='mediumorchid', ls='-.', lw=2, label=r'$\varepsilon=0.01$')
    # plt.scatter(x_list, mean, color='darkcyan', label=r'$\varepsilon=0.01$', facecolor='none', marker='D')
    # plt.fill_between(x_list, mean - std, mean + std, color='darkcyan', lw=0, alpha=0.4)

    setattr(arguments, 'mc_steps', 1001)

    systems_res = defaultdict(DefDict)
    for i, z in enumerate(z_list):
        setattr(arguments, 'n_zealots', z)
        cfg = Config(arguments, parser._option_string_actions)
        res, settings = read_data('_basic_z' + cfg.suffix, input_dir='results/final3/')
        distribution = convert_to_distributions(res[system])
        systems_res[system]['mean'].append(np.mean(distribution['a']))
        systems_res[system]['std'].append(np.std(distribution['a']))
    mean = np.array(systems_res[system]['mean'])
    std = np.array(systems_res[system]['std'])
    plt.plot(x_list, mean, color='darkorange', ls=':', lw=2, label=r'$r=0.007$')
    # plt.scatter(x_list, mean, color='darkorange', label=r'$r=0.007$', facecolor='none', marker='v')
    # plt.fill_between(x_list, mean - std, mean + std, color='darkorange', lw=0, alpha=0.4)

    setattr(arguments, 'mc_steps', 1002)
    setattr(arguments, 'num_parties', 6)

    systems_res = defaultdict(DefDict)
    for i, z in enumerate(z_list):
        setattr(arguments, 'n_zealots', z)
        cfg = Config(arguments, parser._option_string_actions)
        res, settings = read_data('_basic_z' + cfg.suffix, input_dir='results/final3/')
        distribution = convert_to_distributions(res[system])
        systems_res[system]['mean'].append(np.mean(distribution['a']))
        systems_res[system]['std'].append(np.std(distribution['a']))
    mean = np.array(systems_res[system]['mean'])
    std = np.array(systems_res[system]['std'])
    plt.plot(x_list, mean, color='goldenrod', ls=(0, (3, 1, 1, 1, 1, 1)), lw=2, label='6 parties')
    # plt.scatter(x_list, mean, color='goldenrod', label='6 parties', facecolor='none', marker='s')
    # plt.fill_between(x_list, mean - std, mean + std, color='goldenrod', lw=0, alpha=0.4)

    plt.title('PV')
    plt.title('i', loc='left', fontweight='bold')
    plt.xlabel('% of zealots')
    plt.ylabel('fraction of seats')
    plt.legend(loc='best', bbox_to_anchor=(1, 0.95))

    plt.xlim([0, 2])
    plt.ylim([0.13, 1.005])

    plt.tight_layout()
    plt.savefig(f'plots/z_sus_pv.pdf')
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

    main('100 districts FPTP', arguments=args)

