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
from tools import read_data


def main():
    os.chdir(parentdir)

    args = parser.parse_args()
    setattr(args, 'n', 10000)
    setattr(args, 'q', 100)
    setattr(args, 'sample_size', 1000)
    setattr(args, 'mc_steps', 50)
    setattr(args, 'therm_time', 5000000)
    setattr(args, 'seats', [5])
    setattr(args, 'ratio', 0.002)
    setattr(args, 'avg_deg', 12)
    setattr(args, 'epsilon', 0.005)
    setattr(args, 'num_parties', 3)

    eps_list = [0.000001, 0.005, 0.1]
    number = ['d', 'c', 'b']
    for i, epsilon in enumerate(eps_list):
        setattr(args, 'epsilon', epsilon)
        cfg = Config(args, parser._option_string_actions)
        res, settings = read_data('_trajectory'+cfg.suffix, input_dir='results/final3/traj/')

        plt.figure(figsize=(3.5, 2.7))
        plt.plot(res['a'], label='party a', color='mediumorchid')
        plt.plot(res['b'], label='party b', color='darkcyan')
        plt.plot(res['c'], label='party c', color='darkorange')

        ax = plt.gca()
        if i == 0:
            plt.text(0.85, 0.865, r'$\varepsilon=10^{-6}$', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        else:
            plt.text(0.85, 0.865, r'$\varepsilon=$'+f'{epsilon}', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)

        plt.legend(fontsize=9, loc=2)

        plt.title(number[i], loc='left', fontweight='bold')
        plt.xlabel('time')
        plt.ylabel('fraction of voters')
        plt.xlim([0, 100])
        plt.ylim([0, 1])

        plt.tight_layout()
        plt.savefig(f'plots/traj_eps_{str(epsilon)[2:]}.pdf')
        plt.close()

    setattr(args, 'epsilon', 0.00001)
    cfg = Config(args, parser._option_string_actions)
    res, settings = read_data('_trajectory' + cfg.suffix, input_dir='results/final3/traj/')

    day = 68

    plt.figure(figsize=(6.5, 4))
    plt.plot(res['a'][:day+1], label='party a', color='mediumorchid', alpha=1, lw=2)
    plt.plot(res['b'][:day+1], label='party b', color='darkcyan', alpha=1, lw=2)
    plt.plot(res['c'][:day+1], label='party c', color='darkorange', alpha=1, lw=2)
    plt.plot(range(day, 101), res['a'][day:], color='mediumorchid', alpha=0.5, lw=2)
    plt.plot(range(day, 101), res['b'][day:], color='darkcyan', alpha=0.5, lw=2)
    plt.plot(range(day, 101), res['c'][day:], color='darkorange', alpha=0.5, lw=2)

    print(res['a'][day], res['b'][day], res['c'][day])

    plt.axvline(day, ls='-', lw=1, color='black')
    plt.text(66.3, 0.65, 'election day', horizontalalignment='center', verticalalignment='center', rotation=90)
    plt.text(84, 0.65, 'obtained votes:\nparty a - 49%\nparty b - 33%\nparty c - 18%', horizontalalignment='center', verticalalignment='center')

    plt.text(101, 0.495, '0.49', horizontalalignment='left', verticalalignment='center')
    plt.text(101, 0.327, '0.33', horizontalalignment='left', verticalalignment='center')
    plt.text(101, 0.179, '0.18', horizontalalignment='left', verticalalignment='center')

    plt.plot([day, 100], [0.495, 0.495], ls='--', lw=0.8, color='black')
    plt.plot([day, 100], [0.327, 0.327], ls='--', lw=0.8, color='black')
    plt.plot([day, 100], [0.179, 0.179], ls='--', lw=0.8, color='black')

    plt.legend(fontsize=9, loc=2)

    plt.title('a', loc='left', fontweight='bold')
    plt.xlabel('time')
    plt.ylabel('fraction of voters')
    plt.xlim([0, 100])
    plt.ylim([0.1, 0.8])

    plt.tight_layout()
    plt.savefig(f'plots/traj_election.pdf')
    plt.close()


if __name__ == '__main__':
    main()

