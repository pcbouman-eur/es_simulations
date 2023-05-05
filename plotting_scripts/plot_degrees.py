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
from plotting_scripts.plotting_tools import names_dict, DefDict, plot_box


def main():
    param = 'degree'
    os.chdir(parentdir)

    args = parser.parse_args()
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

    systems_res = defaultdict(DefDict)

    k_list = [6, 9, 12, 15, 18, 25, 50]
    for k in k_list:
        setattr(args, 'avg_deg', float(k))
        cfg = Config(args, parser._option_string_actions)
        res, settings = read_data(cfg.suffix, input_dir='results/final1/')
        voting_distribution = convert_to_distributions(res['vote_fractions'])

        for system in ['countrywide_system', 'main_district_system', '100 districts Webster', '100 districts FPTP']:
            distribution = convert_to_distributions(res[system])
            systems_res[system]['data'].append(distribution['a'])
            systems_res[system]['mean'].append(np.mean(distribution['a']))
            systems_res[system]['std'].append(np.std(distribution['a']))

            indexes = calculate_indexes(voting_distribution, distribution, cfg.sample_size)
            systems_res[system]['gall'].append(indexes['Gallagher index'])
            systems_res[system]['loos'].append(indexes['Loosemore Hanby index'])
            systems_res[system]['eff'].append(indexes['Eff. No of Parties'])

    res = systems_res['main_district_system']
    short = names_dict['main_district_system']["short"]
    plot_box(res['data'], labels=k_list, file_name=f'{param}_box_{short.lower()}.pdf', title=short, number='b', ylabel='fraction of seats', xlabel=f'average {param}', ylim=(-0.03, 1.03))
    plot_box(res['gall'], labels=k_list, file_name=f'{param}_box_{short.lower()}_gall.pdf', title=short, number='d', ylabel='Gallagher index', xlabel=f'average {param}', ylim=(-0.002, 0.088))
    plot_box(res['loos'], labels=k_list, file_name=f'{param}_box_{short.lower()}_loos.pdf', title=short, number='e', ylabel='Loosemore-Hanby index', xlabel=f'average {param}', ylim=(-0.002, 0.088))
    plot_box(res['eff'], labels=k_list, file_name=f'{param}_box_{short.lower()}_eff.pdf', title=short, number='f', ylabel='effective num. of parties', xlabel=f'average {param}', ylim=(1.45, 3.05))

    res = systems_res['100 districts FPTP']
    short = names_dict['100 districts FPTP']["short"]
    plot_box(res['data'], labels=k_list, file_name=f'{param}_box_{short.lower()}.pdf', title=short, number='c', ylabel='fraction of seats', xlabel=f'average {param}', ylim=(-0.03, 1.03))
    plot_box(res['gall'], labels=k_list, file_name=f'{param}_box_{short.lower()}_gall.pdf', title=short, number='g', ylabel='Gallagher index', xlabel=f'average {param}', ylim=(-0.015, 0.42))
    plot_box(res['loos'], labels=k_list, file_name=f'{param}_box_{short.lower()}_loos.pdf', title=short, number='h', ylabel='Loosemore-Hanby index', xlabel=f'average {param}', ylim=(-0.015, 0.42))
    plot_box(res['eff'], labels=k_list, file_name=f'{param}_box_{short.lower()}_eff.pdf', title=short, number='i', ylabel='effective num. of parties', xlabel=f'average {param}', ylim=(0.95, 3.05))

    fig = plt.figure(figsize=(6, 5))
    axs = fig.subplots(3, 3)
    index = 0
    for i, ax_col in enumerate(axs):
        for j, ax in enumerate(ax_col):
            ax.set_xlim([0, 1])
            ax.set_ylim([0, 5])
            ax.set_xticks((0, 0.5, 1))
            for system in ['main_district_system', '100 districts FPTP']:
                color = 'deepskyblue' if system == 'main_district_system' else 'orangered'
                ax.hist(systems_res[system]['data'][index], bins=np.linspace(0.0, 1.0, 26), range=(0, 1), density=True, color=color, alpha=0.7)
            if i == 0 or (i == 1 and j == 0):
                ax.set_xticklabels(())
            else:
                ax.set_xticklabels((0, 0.5, 1))
            if j != 0:
                ax.set_yticklabels(())
            ax.text(0.65, 4.3, r'$k=$'+f'{k_list[index]}')
            index += 1
            if index > 6:
                break

    plt.subplots_adjust(wspace=0.09, hspace=0.08, top=0.96, bottom=0.09, left=0.08, right=0.97)
    axs[0][0].set_title('a', loc='left', fontweight='bold')
    axs[2][1].remove()
    axs[2][2].remove()
    axs[2][0].set_xlabel('fraction of seats')
    axs[1][0].set_ylabel('probability')
    axs[1][1].text(0.8, 2.23, 'PR', bbox=dict(facecolor='deepskyblue', edgecolor='none', pad=2.0, alpha=0.7))
    axs[1][1].text(0.8, 1.55, 'PV', bbox=dict(facecolor='orangered', edgecolor='none', pad=2.0, alpha=0.7))
    plt.savefig(f'plots/{param}_hist.pdf')
    plt.show()
    plt.close()


if __name__ == '__main__':
    main()
