# -*- coding: utf-8 -*-
import os
import sys
import inspect
import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import minimize

# path hack for imports to work when running this script from any location,
# without the hack one has to manually edit PYTHONPATH every time
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

# country for which the optimisation should be made
country = "Israel"  # "Israel", "India", "Poland"

x_m = 1.0


def affinity_integral(x, c):
    """
    Returns normalised integral (antiderivative) of the affinity matrix probabilities as a function of distance.
    :param x: distance (float)
    :param c: constant in the function describing link probability for planar graph generator (float)
    :return: antiderivative of the affinity matrix probabilities (float)
    """
    # return -c**2.0 / (x + c)**2.0
    return -x_m**c / x**c


def objective_function(c, data):
    """
    Computes the average square difference between the data and affinity prediction.
    :param c: constant in the function describing link probability for planar graph generator (float)
    :param data: distance -- first row -- and percentage of population -- second row (np.array)
    :return: mean square error between data and affinity prediction (float)
    """
    affinity = affinity_integral(data[0, 1:], c) - affinity_integral(data[0, :-1], c)
    objective = np.mean((affinity - data[1, 1:])**2.0)
    return objective


if __name__ == '__main__':
    if country == "Israel":
        data = np.array([[x_m, 5, 10, 20, 40, np.inf],
                         [0.0, 0.505, 0.143, 0.165, 0.121, 0.066]])
    elif country == "India":
        ...
    elif country == "Poland":
        ...
    else:  # exampla data
        data = np.array([[x_m, 5, 10, 20, 30, 40, np.inf],
                         [0.0, 0.4, 0.2, 0.1, 0.1, 0.1, 0.1]])

    c0 = 0.1
    limits = ([0.0, None], )
    res = minimize(objective_function, x0=c0, args=(data, ), bounds=limits)

    print("Objective:         ", np.round(objective_function(res.x[0], data), 4))
    print("Optimal parameter: ", np.round(res.x[0], 4))

    # Plotting original data and fit
    x = data[0, :-1]
    heights = data[1, 1:] / data[1, 1:].sum()
    widths = data[0, 1:-1] - data[0, :-2]
    widths = np.append(widths, widths[-1])

    heights_approx = affinity_integral(data[0, 1:], res.x[0]) - affinity_integral(data[0, :-1], res.x[0])

    z = np.linspace(x_m, data[0, -2] + widths[-1], 300)
    y = res.x[0] * x_m**res.x[0] / z**(res.x[0]+1)
    
    plt.bar(x, height=heights, width=widths, align="edge", alpha=0.5, label="data")
    plt.bar(x, height=heights_approx, width=widths, align="edge", alpha=0.5, label="optimal probabilities")
    plt.plot(z, y, "r--", label="optimal affinity function")

    plt.ylabel("Probability")
    plt.ylabel("Distance (km)")
    plt.xlim(0.0, data[0, -2] + widths[-1])
    plt.axhline(0.0, ls="--", lw=1, c="gray")
    plt.legend()

    plt.show()
