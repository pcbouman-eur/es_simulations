import os
import sys
import inspect
import numpy as np
from matplotlib import pyplot as plt
from collections import defaultdict


names_dict = {
    'main_district_system': {
        'short': 'PR',
        'medium': 'PR Jefferson',
        'long': 'proportional representation with the Jefferson method',
    },
    'countrywide_system': {
        'short': 'global-PR',
        'medium': 'PR one district',
        'long': 'proportional representation with one countrywide district',
    },
    '100 districts Webster': {
        'short': 'PR-W',
        'medium': 'PR Webster',
        'long': 'proportional representation with the Webster method',
    },
    '100 districts FPTP': {
        'short': 'PV',
        'medium': 'PV',
        'long': 'plurality voting',
    },
}


class DefDict(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__setitem__('data', [])
        self.__setitem__('gall', [])
        self.__setitem__('loos', [])
        self.__setitem__('eff', [])
        self.__setitem__('mean', [])
        self.__setitem__('std', [])


def plot_box(data, labels=None, file_name=None, title=None, number=None, ylabel=None, xlabel=None, ylim=None):
    outlier_marker = dict(markerfacecolor='none', marker='o', markeredgecolor='sandybrown', alpha=0.1)
    meanprops = dict(markerfacecolor='none', marker='x', markeredgecolor='gray', alpha=0.9, markersize=4)

    plt.figure(figsize=(3.5, 2.7))
    plt.boxplot(data, flierprops=outlier_marker, labels=labels, showmeans=True, meanprops=meanprops)
    plt.title(title)
    plt.title(number, loc='left', fontweight='bold')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.ylim(ylim)

    plt.tight_layout()
    plt.savefig(f'plots/{file_name}')
    plt.close()


