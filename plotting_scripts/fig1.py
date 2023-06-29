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
from tools import read_data, convert_to_distributions, calculate_indexes


cm = 1/2.54  # centimeters in inches


def main():
    os.chdir(parentdir)

    plt.rcParams.update({'font.size': 7})
    title_font = 8

    gs_kw = dict(width_ratios=[1, 1], height_ratios=[1.8, 1, 1])
    fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(8.7*cm, 12*cm), gridspec_kw=gs_kw)
    gs = axs[0, 0].get_gridspec()
    for ax in axs[0, 0:]:
        ax.remove()
    axbig = fig.add_subplot(gs[0, 0:])

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################

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
    setattr(args, 'epsilon', 0.00001)
    cfg = Config(args, parser._option_string_actions)
    res, settings = read_data('_trajectory' + cfg.suffix, input_dir='results/final3/traj/')

    day = 68
    axbig.plot(res['a'][:day+1], label=r'party $a$', color='mediumorchid', alpha=1, lw=1)
    axbig.plot(res['b'][:day+1], label=r'party $b$', color='darkcyan', alpha=1, lw=1)
    axbig.plot(res['c'][:day+1], label=r'party $c$', color='darkorange', alpha=1, lw=1)
    axbig.plot(range(day, 101), res['a'][day:], color='mediumorchid', alpha=0.3, lw=1)
    axbig.plot(range(day, 101), res['b'][day:], color='darkcyan', alpha=0.3, lw=1)
    axbig.plot(range(day, 101), res['c'][day:], color='darkorange', alpha=0.3, lw=1)

    axbig.axvline(day, ls='-', lw=0.8, color='black')
    axbig.text(65.8, 0.648, 'election day', horizontalalignment='center', verticalalignment='center', rotation=90)
    axbig.text(84, 0.65, 'obtained votes:\nparty '+'$a$'+' - 49%\nparty '+r'$b$'+' - 33%\nparty '+r'$c$'+' - 18%', horizontalalignment='center', verticalalignment='center')

    axbig.text(69, 0.465, '0.49', horizontalalignment='left', verticalalignment='center')
    axbig.text(69, 0.293, '0.33', horizontalalignment='left', verticalalignment='center')
    axbig.text(69, 0.145, '0.18', horizontalalignment='left', verticalalignment='center')

    axbig.plot([day, 100], [0.495, 0.495], ls='--', lw=0.5, color='black', zorder=-10)
    axbig.plot([day, 100], [0.327, 0.327], ls='--', lw=0.5, color='black', zorder=-10)
    axbig.plot([day, 100], [0.179, 0.179], ls='--', lw=0.5, color='black', zorder=-10)

    axbig.legend(loc=2)

    axbig.set_title('a', loc='left', fontweight='bold', fontsize=title_font)
    axbig.set_xlabel('time [5 MC steps]')
    axbig.set_ylabel('fraction of voters')
    axbig.set_xlim([0, 100])
    axbig.set_ylim([0.1, 0.8])

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################

    setattr(args, 'n', 10000)
    setattr(args, 'q', 100)
    setattr(args, 'sample_size', 4000)
    setattr(args, 'mc_steps', 50)
    setattr(args, 'therm_time', 10000000)
    setattr(args, 'seats', [5])
    setattr(args, 'ratio', 0.002)
    setattr(args, 'avg_deg', 12.0)
    setattr(args, 'epsilon', 0.005)
    setattr(args, 'num_parties', 3)
    cfg = Config(args, parser._option_string_actions)
    res, settings = read_data(cfg.suffix, input_dir='results/final1/')
    voting_distribution = convert_to_distributions(res['vote_fractions'])

    axs[1, 0].axvline(1. / 3, ls='-', lw=0.8, color='black', zorder=-10)
    axs[1, 0].hist(voting_distribution['a'], bins=np.linspace(0.0, 1.0, 25), range=(0, 1), density=True, color='mediumorchid', alpha=0.9)
    axs[1, 0].set_xlim([0, 1])
    axs[1, 0].set_xlabel('fraction of votes')
    axs[1, 0].set_ylabel('probability')
    axs[1, 0].set_title('b', loc='left', fontweight='bold', fontsize=title_font)
    axs[1, 0].set_xticks((0, 1./3, 2./3, 1))
    axs[1, 0].set_xticklabels((0, 0.33, 0.66, 1))
    axs[1, 0].text(0.6, 4, r'party $a$', horizontalalignment='left', verticalalignment='center')

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################

    for system in ['main_district_system', '100 districts FPTP']:
        distribution = convert_to_distributions(res[system])
        color = 'deepskyblue' if system == 'main_district_system' else 'orangered'
        axs[1, 1].axvline(1. / 3, ls='-', lw=0.8, color='black', zorder=-10)
        axs[1, 1].hist(distribution['a'], bins=np.linspace(0.0, 1.0, 25), range=(0, 1), density=True, color=color, alpha=0.7)
        axs[1, 1].set_xlim([0, 1])
        axs[1, 1].set_ylim([0, 6.2])
        axs[1, 1].set_xlabel('fraction of seats')
        axs[1, 1].set_ylabel('probability')
        axs[1, 1].set_title('c', loc='left', fontweight='bold', fontsize=title_font)
        axs[1, 1].set_xticks((0, 1. / 3, 2. / 3, 1))
        axs[1, 1].set_xticklabels((0, 0.33, 0.66, 1))

        axs[1, 1].text(0.7, 3.5, 'PR', bbox=dict(facecolor='deepskyblue', edgecolor='none', pad=2.0, alpha=0.5))
        axs[1, 1].text(0.7, 2.359, 'PV', bbox=dict(facecolor='orangered', edgecolor='none', pad=2.0, alpha=0.5))

        ################################################################################################################

        indexes = calculate_indexes(voting_distribution, distribution, cfg.sample_size)
        color = 'deepskyblue' if system == 'main_district_system' else 'orangered'
        axs[2, 0].hist(indexes['Gallagher index'], bins=np.linspace(0.0, 0.3, 25), range=(0, 0.3), density=True, color=color, alpha=0.7)
        axs[2, 0].set_xlim([0, 0.3])
        axs[2, 0].set_xlabel('Gallagher index')
        axs[2, 0].set_ylabel('probability')
        axs[2, 0].set_title('d', loc='left', fontweight='bold', fontsize=title_font)

        # axs[2, 0].text(0.2, 22.5, 'PR', bbox=dict(facecolor='deepskyblue', edgecolor='none', pad=2.0, alpha=0.5))
        # axs[2, 0].text(0.2, 16.2, 'PV', bbox=dict(facecolor='orangered', edgecolor='none', pad=2.0, alpha=0.5))
        axs[2, 0].text(0.07, 24, 'disproportionality')

        ################################################################################################################

        axs[2, 1].hist(indexes['Eff. No of Parties'], bins=np.linspace(1, 3, 25), range=(1, 3), density=True, color=color, alpha=0.7)
        axs[2, 1].set_xlim([1, 3])
        axs[2, 1].set_xlabel('eff. num. of parties')
        axs[2, 1].set_ylabel('probability')
        axs[2, 1].set_title('e', loc='left', fontweight='bold', fontsize=title_font)

        # axs[2, 1].text(1.5, 2.9, 'PR', bbox=dict(facecolor='deepskyblue', edgecolor='none', pad=2.0, alpha=0.5))
        # axs[2, 1].text(1.5, 2.1, 'PV', bbox=dict(facecolor='orangered', edgecolor='none', pad=2.0, alpha=0.5))
        axs[2, 1].text(1.2, 2.7, 'political\nfragmentation')

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################

    plt.subplots_adjust(left=0.125, right=0.97, top=0.965, bottom=0.075, hspace=0.53, wspace=0.35)
    plt.savefig(f'plots/fig1.pdf')
    plt.close()


if __name__ == '__main__':
    main()

