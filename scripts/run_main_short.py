import matplotlib as mpl
mpl.use('agg')
import os
import sys
import inspect

# path hack for imports to work when running this script from any location,
# without the hack one has to manually edit PYTHONPATH every time
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from configuration.parser import get_arguments


if __name__ == '__main__':
    os.chdir(parentdir)
    cfg = get_arguments()

    parties = 3
    ra = 0.002
    k = 12
    e = 0.005
    qs = 5

    file_name = f'script_basic_merging.sh'
    out_file = f'log/out_basic_merging.txt'
    er_file = f'log/error_basic_merging.txt'
    with open(file_name, 'w') as _file:
        _file.write(f'/home/tomasz/anaconda2/envs/conda_python3.6/bin/python3 main.py '
                    f'--config_file {cfg.config_file} -qs {qs} -avg_deg {k} -ra {ra} -e {e} -np {parties}')
    os.system(f'run -t 70:00 -o {out_file} -e {er_file} bash {file_name}')
