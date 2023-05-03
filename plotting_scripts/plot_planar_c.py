import os
import sys
import inspect
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# path hack for imports to work when running this script from any location,
# without the hack one has to manually edit PYTHONPATH every time
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


Israel = np.array([[0, 5, 10, 20, 40, 80],
                   [0.0, 0.505, 0.143, 0.165, 0.121, 0.066]])
India = np.array([[0, 1, 5, 10, 20, 30, 50, 100],
                  [0.0, 0.2391093895, 0.3345624697, 0.2001085192, 0.09743021074, 0.05492006168, 0.03557149438,
                   0.03829785485]])
Poland = np.array([[0, 5, 10, 15, 20, 30, 40, 60, 80, 100, 630],
                   [0.0, 0.7315281676792722, 0.04877240795194137, 0.06853774559525151, 0.044917292501255084,
                    0.037084754908489836, 0.016260173013807635, 0.01888197596385357, 0.008741833413590428,
                    0.0048085953642135314, 0.02046705360832488]])


def affinity_integral(x, c):
    return -c / (x + c)


def objective_function(c, data):
    affinity = affinity_integral(data[0, 1:], c) - affinity_integral(data[0, :-1], c)
    objective = np.mean((affinity - data[1, 1:])**2.0)
    return objective


def plot_fit(data, name):
    c0 = 0.1
    limits = ([0.0, None], )
    res = minimize(objective_function, x0=c0, args=(data, ), bounds=limits)

    heights = data[1, 1:] / data[1, 1:].sum()
    heights_approx = affinity_integral(data[0, 1:], res.x[0]) - affinity_integral(data[0, :-1], res.x[0])
    r_sqr = 1.0 - (np.sum((heights - heights_approx) ** 2.0) / np.sum((heights - np.mean(heights)) ** 2.0))

    print("Mean squared error: ", np.round(objective_function(res.x[0], data), 4))
    print("Pseudo R^2:         ", np.round(r_sqr, 4))
    print("Optimal parameter:  ", np.round(res.x[0], 4))

    # Plotting original data and fit
    x = data[0, :-1]
    widths = data[0, 1:-1] - data[0, :-2]
    widths = np.append(widths, widths[-1])

    z = np.linspace(0.0, data[0, -2] + widths[-1], 300)
    y = res.x[0] / (z + res.x[0])**2.0

    plt.figure(figsize=(6, 3.5))

    a = plt.bar(x, height=heights, width=widths, color='darkorange', align="edge", alpha=0.6, label="commuting data")
    b = plt.bar(x, height=heights_approx, width=widths, color='darkcyan', align="edge", alpha=0.6, label="optimal probabilities")

    for _x in x[1:]:
        plt.axvline(_x, color='white', linewidth=1)

    c, = plt.plot(z, y, ls="--", color='black', label="optimal affinity function")

    plt.title('d', loc='left', fontweight='bold', fontsize=14)
    plt.ylabel("probability")
    plt.xlabel("commuting distance [km]")
    plt.xlim(0.0, data[0, -2] + widths[-1])
    plt.legend(handles=[a, b, c], loc=1)
    plt.tight_layout()

    # inset for poland
    if name == 'pl':
        ax = plt.gca()
        axin = inset_axes(ax, width="100%", height="100%", bbox_to_anchor=(.4, .25, .4, .4), bbox_transform=ax.transAxes)
        axin.bar(x, height=heights, width=widths, color='darkorange', align="edge", alpha=0.6, label="commuting data")
        axin.bar(x, height=heights_approx, width=widths, color='darkcyan', align="edge", alpha=0.6, label="optimal probabilities")
        for _x in x[1:]:
            axin.axvline(_x, color='white', linewidth=1)
        axin.plot(z, y, ls="--", color='black', label="optimal affinity function")
        axin.set_xlim(0.0, data[0, -2] + widths[-1])
        axin.set_yscale('log')
        # axin.set_ylim([0., 0.027])

    os.chdir(parentdir)
    plt.savefig(f'plots/{name}_planar_c.pdf')
    plt.show()


if __name__ == '__main__':
    for d, n in [(Poland, 'pl'), (India, 'ind'), (Israel, 'il')]:
        plot_fit(d, n)

