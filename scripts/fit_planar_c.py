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


def affinity_integral(x, c):
    """
    Returns normalised integral (antiderivative) of the affinity matrix probabilities as a function of distance.
    :param x: distance (float)
    :param c: constant in the function describing link probability for planar graph generator (float)
    :return: antiderivative of the affinity matrix probabilities (float)
    """
    return -c**2.0 / (x + c)**2.0
    # return np.log(x + c)


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
    print("work in progress...")

    if country == "Israel":
        data = np.array([[0, 5, 10, 20, 40, np.inf],
                         [0.0, 0.505, 0.143, 0.165, 0.121, 0.066]])
    elif country == "India":
        ...
    elif country == "Poland":
        ...
    else:  # exampla data
        data = np.array([[0, 5, 10, 20, 30, 40, np.inf],
                         [0.0, 0.4, 0.2, 0.1, 0.1, 0.1, 0.1]])

    c0 = 0.01
    limits = ([0.0, None], )
    res = minimize(objective_function, x0=c0, args=(data, ), bounds=limits)

    print(objective_function(res.x, data))
    print(res.x[0])

    # Plotting original data and fit
    plt.plot(data[0, :-1], data[1, 1:], "ro", label="data")
    plt.plot(data[0, :-1], affinity_integral(data[0, 1:], res.x[0]) -
             affinity_integral(data[0, :-1], res.x[0]), "bx", label="fit")
    plt.legend()
    plt.show()

    # x = np.linspace(0.0, data[0, -2], 300)
    # plt.step(data[0, :-2], data[1, 1:-1] * (data[0, 1:-1]-data[0, :-2]), label="data", where="post")
    # plt.plot(x, 2.0 * res.x[0]**2.0 / (x + res.x[0]))
    # plt.legend()
    # plt.show()

# TODO:
# - correct antiderivative is a log function
# - there is a problem of infinite integral of 1/x (!!!)
