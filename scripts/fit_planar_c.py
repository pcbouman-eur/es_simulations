# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize


Israel = np.array([[0, 5, 10, 20, 40, 80],
                   [0.0, 0.505, 0.143, 0.165, 0.121, 0.066]])
India = np.array([[0, 1, 5, 10, 20, 30, 50, 100],
                  [0.0, 0.2391093895, 0.3345624697, 0.2001085192, 0.09743021074, 0.05492006168, 0.03557149438,
                   0.03829785485]])
Poland = np.array([[0, 5, 10, 15, 20, 30, 40, 60, 80, 100, 630],
                   [0.0, 0.7315281676792722, 0.04877240795194137, 0.06853774559525151, 0.044917292501255084,
                    0.037084754908489836, 0.016260173013807635, 0.01888197596385357, 0.008741833413590428,
                    0.0048085953642135314, 0.02046705360832488]])

# country for which the optimisation should be made
data = Israel  # Israel, India, Poland


def affinity_integral(x, c):
    """
    Returns normalised integral (antiderivative) of the affinity matrix probabilities as a function of distance.
    :param x: distance (float)
    :param c: constant in the function describing link probability for planar graph generator (float)
    :return: antiderivative of the affinity matrix probabilities (float)
    """
    # return -c**3.0 / (x + c)**3.0
    # return -c**2.0 / (x + c)**2.0
    return -c / (x + c)


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
    c0 = 0.1
    limits = ([0.0, None], )
    res = minimize(objective_function, x0=c0, args=(data, ), bounds=limits)

    heights = data[1, 1:] / data[1, 1:].sum()
    heights_approx = affinity_integral(data[0, 1:], res.x[0]) - affinity_integral(data[0, :-1], res.x[0])
    r_sqr = np.sum((heights - np.mean(heights)) ** 2.0) / np.sum((heights_approx - np.mean(heights)) ** 2.0)

    print("Avg. square diff:  ", np.round(objective_function(res.x[0], data), 4))
    print("R^2:               ", np.round(r_sqr, 4))
    print("Optimal parameter: ", np.round(res.x[0], 4))

    # Plotting original data and fit
    x = data[0, :-1]
    widths = data[0, 1:-1] - data[0, :-2]
    widths = np.append(widths, widths[-1])
    widths = widths - (data[0, -2] + widths[-1]) / 200

    z = np.linspace(0.0, data[0, -2] + widths[-1], 300)
    y = res.x[0] / (z + res.x[0])**2.0
    
    plt.bar(x, height=heights, width=widths, align="edge", alpha=0.5, label="data")
    plt.bar(x, height=heights_approx, width=widths, align="edge", alpha=0.5, label="optimal probabilities")
    plt.plot(z, y, "r--", label="optimal affinity function")

    plt.ylabel("Probability")
    plt.ylabel("Distance (km)")
    plt.xlim(0.0, data[0, -2] + widths[-1])
    plt.legend()

    plt.show()
