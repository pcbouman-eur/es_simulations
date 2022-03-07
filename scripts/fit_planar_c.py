# -*- coding: utf-8 -*-
# import matplotlib.pyplot as plt
import os
import sys
import inspect

# path hack for imports to work when running this script from any location,
# without the hack one has to manually edit PYTHONPATH every time
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

# parameters of simulations not present in the config module
m = 20  # the number of bins in the histogram

if __name__ == '__main__':
    print("work in progress...")
