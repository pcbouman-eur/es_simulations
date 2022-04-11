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

Israel = np.array([[0, 5, 10, 20, 40, 400],
                   [0.0, 0.505, 0.143, 0.165, 0.121, 0.066]])
India = np.array([[0, 1, 5, 10, 20, 30, 50, 100],
                  [0.0, 0.2391093895, 0.3345624697, 0.2001085192, 0.09743021074, 0.05492006168, 0.03557149438, 0.03829785485]])
Poland = np.array([[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130,
                    135, 140, 145, 150, 155, 160, 165, 170, 175, 180, 185, 190, 195, 200, 205, 210, 215, 220, 225, 230, 235, 240, 245,
                    250, 255, 260, 265, 270, 275, 280, 285, 290, 295, 300, 305, 310, 315, 320, 325, 330, 335, 340, 345, 350, 355, 360,
                    365, 370, 375, 380, 385, 390, 395, 400, 405, 410, 415, 420, 425, 430, 435, 440, 445, 450, 455, 460, 465, 470, 475,
                    480, 485, 490, 495, 500, 505, 510, 515, 520, 525, 530, 535, 540, 545, 550, 555, 565, 630],
                   [0.0, 69.3999971 + 3.752819671, 4.877240795, 6.85377456, 4.49172925, 2.329344812, 1.379130679, 0.9316866968,
                    0.6943306046, 0.6198579962, 0.5123860605, 0.4434951624, 0.3124583773, 0.2979437961, 0.2336313945,
                    0.1807172081, 0.1618909426, 0.1609410913, 0.1201935391, 0.1131923882, 0.08653251778, 0.09142051645,
                    0.07068387584, 0.06231664669, 0.07959540178, 0.05176155788, 0.04376786574, 0.04751390838, 0.03393850599,
                    0.04698028408, 0.03409859328, 0.04229506265, 0.03782329095, 0.03006439351, 0.02340476215, 0.02974421893,
                    0.02588077894, 0.02542186203, 0.02974421893, 0.02587010645, 0.02148371464, 0.02247625585, 0.0286876428,
                    0.01977611685, 0.02138766226, 0.02566732921, 0.0323909955, 0.02479218535, 0.02952009672, 0.04544344607,
                    0.03504844455, 0.08791994099, 0.05327705091, 0.06181503984, 0.03520853184, 0.04325558641, 0.03154786909,
                    0.06815449662, 0.05587046505, 0.04203892298, 0.0358595535, 0.01928518249, 0.07351208467, 0.02431192347,
                    0.01562451974, 0.02050184591, 0.01041634649, 0.006478199099, 0.01247613632, 0.01061912373, 0.008025709592,
                    0.01492013565, 0.00750275777, 0.009274390473, 0.01060845124, 0.008943543402, 0.01550712239, 0.004482444187,
                    0.007758897438, 0.009743979864, 0.007598810146, 0.002934933694, 0.005549692803, 0.004845308717,
                    0.005218845732, 0.007652172577, 0.006841063629, 0.002902916235, 0.00602995468, 0.005154810815,
                    0.00322309082, 0.01304177809, 0.00639281921, 0.00372469767, 0.0030843485, 0.001985082426, 0.00211315226,
                    0.0003521920433, 0.002582741651, 0.001088593588, 0.001067248616, 0.0002454671817, 0.002561396678,
                    0.0003948819879, 0.0007790914897, 0.0006937116004, 0.00161154541, 0.0007577465174, 0.0006190041973,
                    0.000266812154, 0.0002881571263, 0.0007150565727, 0.0001280698339, 0.0003201745848]])
Poland[1, :] /= Poland[1, :].sum()

# country for which the optimisation should be made
data = India  # "Israel", "India", "Poland"


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

    print("Objective:         ", np.round(objective_function(res.x[0], data), 4))
    print("Optimal parameter: ", np.round(res.x[0], 4))

    # Plotting original data and fit
    x = data[0, :-1]
    heights = data[1, 1:] / data[1, 1:].sum()
    widths = data[0, 1:-1] - data[0, :-2]
    widths = np.append(widths, widths[-1])
    widths = widths * 0.75#- (data[0, -2] + widths[-1]) / 200

    heights_approx = affinity_integral(data[0, 1:], res.x[0]) - affinity_integral(data[0, :-1], res.x[0])

    z = np.linspace(0.0, data[0, -2] + widths[-1], 300)
    y = res.x[0] / (z + res.x[0])**2.0
    
    plt.bar(x, height=heights, width=widths, align="edge", alpha=0.5, label="data")
    plt.bar(x, height=heights_approx, width=widths, align="edge", alpha=0.5, label="optimal probabilities")
    plt.plot(z, y, "r--", label="optimal affinity function")

    plt.ylabel("Probability")
    plt.ylabel("Distance (km)")
    plt.xlim(0.0, data[0, -2] + widths[-1])
    plt.axhline(0.0, ls="--", lw=1, c="gray")
    plt.legend()

    plt.show()
