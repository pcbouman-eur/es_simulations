# -*- coding: utf-8 -*-
import numpy as np

# parameters of simulations not present in the config module
zn_set = np.arange(61)  # range of considered number of zealots
media_influence = np.arange(0.0, 1.0, 0.2)  # range of considered media influence
bins = 25  # how many bins in heat-map histogram


def plot_media_vs_zealots(config):
    """
    Loads the data files saved by main.py and plots them.
    :param config: Config class from configuration module
    """
    # create suffix with both media and zealots insertable
    parameters_and_values = config.suffix.split('_')
    media_index = parameters_and_values.index('media')
    zealots_index = parameters_and_values.index('zn')
    first_index = min(media_index, zealots_index)
    second_index = max(media_index, zealots_index)
    pre_suffix = '_'.join(parameters_and_values[:first_index])
    inter_suffix = '_'.join(parameters_and_values[first_index:(second_index+2)])
    inter_suffix = '_' + inter_suffix
    su_suffix = '_'.join(parameters_and_values[(second_index+2):])
    if len(su_suffix):
        su_suffix = '_' + su_suffix
    if media_index < zealots_index:
        suffix = pre_suffix + '{media_value}' + inter_suffix + '{zn_value}' + su_suffix
    elif media_index > zealots_index:
        suffix = pre_suffix + '{zn_value}' + inter_suffix + '{media_value}' + su_suffix
    pass


if __name__ == '__main__':
    pass
