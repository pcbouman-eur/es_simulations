# -*- coding: utf-8 -*-
# import matplotlib.pyplot as plt
import os
import sys
import inspect
import numpy as np

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
    else:
        data = np.array([[0, 5, 10, 20, 30, 40, np.inf],
                         [0.0, 0.4, 0.2, 0.1, 0.1, 0.1, 0.1]])

    c0 = 0.01
    limits = ([0.0, None], )
    res = minimize(objective_function, x0=c0, args=(data, ), bounds=limits)

    print(objective_function(res.x, data))
    print(res.x[0])

# TODO:
# - plot (as a test of fit goodness)
