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


def main():
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

    z_list = [0, 13, 26]
    numbers = ['d', 'e', 'f']
    titles = ['no zealots', '~0.1% of zealots', '~0.25% of zealots']
    for i, z in enumerate(z_list):
        setattr(args, 'n_zealots', z)
        cfg = Config(args, parser._option_string_actions)
        res, settings = read_data('_basic_z' + cfg.suffix, input_dir='results/final1/')

        plt.figure(figsize=(3.5, 2.7))
        for system in ['main_district_system', '100 districts FPTP']:
            distribution = convert_to_distributions(res[system])
            color = 'deepskyblue' if system == 'main_district_system' else 'orangered'
            plt.hist(distribution['a'], bins=np.linspace(0.0, 1.0, 23), range=(0, 1), density=True, color=color, alpha=0.7, zorder=10)
            if i != 0:
                plt.axvline(np.mean(distribution['a']), ls='--', lw=1, color='black', zorder=0)

        plt.axvline(1./3, ls='-', lw=0.9, color='black', zorder=0)
        if i == 0:
            plt.text(0.8, 2.5, 'PR', bbox=dict(facecolor='deepskyblue', edgecolor='none', pad=2.0, alpha=0.7))
            plt.text(0.8, 1.86, 'PV', bbox=dict(facecolor='orangered', edgecolor='none', pad=2.0, alpha=0.7))

        plt.title(titles[i])
        plt.title(numbers[i], loc='left', fontweight='bold')
        plt.xlabel('fraction of seats')
        plt.ylabel('probability')

        plt.xlim([0, 1])
        plt.ylim([0, 6])

        plt.tight_layout()
        plt.savefig(f'plots/z_hist_{z}.pdf')
        plt.close()


if __name__ == '__main__':
    main()

