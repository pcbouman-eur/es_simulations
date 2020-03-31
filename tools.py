# -*- coding: utf-8 -*-
from collections import Counter
from collections.abc import Iterable
import numbers


def convert_to_distributions(series, missing_value=0):
    """
    Converts a list of dicts into a dict of lists
    :param series: a list of dicts
    :param missing_value: value to insert if a key in a series
    :result: a dict of lists
    """
    # Compute all keys that occur in the series
    keys = set()
    for d in series:
        keys.update(d.keys())
    res = {k: [d[k] if k in d else missing_value for d in series] for k in keys}
    return res


def prepare_json(d):
    if isinstance(d, dict) or isinstance(d, Counter):
        res = {}
        for k, v in d.items():
            if isinstance(k, numbers.Integral):
                res[str(k)] = prepare_json(v)
            else:
                res[k] = prepare_json(v)
        return res
    if isinstance(d, Iterable):
        return [prepare_json(i) for i in d]
    return d
