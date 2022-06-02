import csv
import os
from os import listdir
from os.path import isfile, join
import numpy as np


log = os.path.abspath('log')
only_files = [join(log, f) for f in listdir(log) if isfile(join(log, f)) and 'error_ind_house_otp_mm' in f]

min_times = []
h_times = []


for file in only_files:
    with open(file, 'r') as in_file:
        content = csv.reader(in_file)

        while True:
            try:
                row = next(content)
                if row[0][-2:] == ' h' or row[0][-4:] == ' min':
                    break
            except StopIteration:
                print('WHY')
                break
        # print(row)

        if 'min' in row[0]:
            minu = row[0][-8:]
            min_num = float(minu[:-4])
            print()
            print(file)
            print(minu)
            min_times.append(min_num)
        else:
            hours = row[0][-6:]
            hours_num = float(hours[:-2])
            print()
            print(file)
            print(hours)
            h_times.append(hours_num)


print()
print()

if min_times:
    print(f'Minute times:')
    print(f'Avg: {np.mean(min_times)} min')
    print(f'Median: {np.median(min_times)} min')
    print(f'Max: {max(min_times)} min')
    print(f'Min: {min(min_times)} min')

if h_times:
    print(f'Hour times:')
    print(f'Avg: {np.mean(h_times)} h')
    print(f'Median: {np.median(h_times)} h')
    print(f'Max: {max(h_times)} h')
    print(f'Min: {min(h_times)} h')

