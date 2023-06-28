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

    m_list = [0.2, None, 0.6]
    numbers = ['a', 'b', 'c']
    titles = ['negative bias', 'no bias', 'positive bias']
    for i, m in enumerate(m_list):
        setattr(args, 'mass_media', m)
        cfg = Config(args, parser._option_string_actions)
        res, settings = read_data('_trajectory' + cfg.suffix, input_dir='results/final3/traj/')

        plt.figure(figsize=(3.5, 2.7))
        plt.plot(res['a'], label=r'media party $a$', color='mediumorchid', lw=2, alpha=1)
        plt.plot(res['b'], label=r'party $b$', color='darkcyan', lw=2, alpha=0.5)
        plt.plot(res['c'], label=r'party $c$', color='darkorange', lw=2, alpha=0.5)

        plt.legend(fontsize=9, loc=2)

        plt.title(titles[i])
        plt.title(numbers[i], loc='left', fontweight='bold')
        plt.xlabel('time')
        plt.ylabel('fraction of voters')
        plt.xlim([0, 100])
        plt.ylim([0, 1])

        plt.tight_layout()
        plt.savefig(f'plots/m_traj_{m}.pdf')
        plt.close()


if __name__ == '__main__':
    main()

