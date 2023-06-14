[![Python tests](https://github.com/pcbouman-eur/wwcs2020-votingmodel/actions/workflows/run_tests.yml/badge.svg)](https://github.com/pcbouman-eur/wwcs2020-votingmodel/actions/workflows/run_tests.yml)

# Electoral Systems project

This is a software for running a simulation of voting processes and on top of that comparing different electoral systems.
It achieves number of things, which are separated in different parts of the repository.
First, it generates a network using either a Stochastic Block Model or an original distance based network model, establishes the initial state of the nodes (voters) and defines zealots (voters who never change their mind).
Second, it runs a dynamical process of opinion formation on top of the created network.
In the course of this process, voters can change their opinions (and therefore votes) due to social interactions (propagation), or independent choices (mutation, or noise).
In the program you can choose to use the noisy voter model or the majority rule to simulate the opinion dynamics (there is also minority rule, but this one is not supported empirically).
Finally, the software performs elections after every given number of steps, collecting the statistics of the election's result and computing several indexes, to later save it and plot it.
The key part of the program is the ability to define an arbitrary type of electoral system to be used and analyzed.
Due to high flexibility and wide parametrization many real-world electoral systems can be simulated and studied.
New measures of the system's stability, like zealot- or media-susceptibility, can be computed using special scripts.
Fell free to use our code, and if you do so, we kindly ask to cite us:

```
@article{wilinski2022vulnerability,
  title={Vulnerability of electoral systems: how to improve the core of democracy},
  author={Wilinski, Mateusz and Klamut, Jaroslaw and Cremades, Roger and Bouman, Paul and Raducha, Tomasz},
  journal={...},
  year={2022}
}
```

## Requirements

[![python](https://img.shields.io/badge/python-3.6%7C3.7%7C3.8%7C3.9%7C3.10-brightgreen)](https://www.python.org/downloads/release/python-360/)
[![python-igraph](https://img.shields.io/badge/python--igraph-0.8-yellowgreen)](https://igraph.org/2020/02/14/igraph-0.8.0-python.html)
[![numpy](https://img.shields.io/badge/numpy-1.19.2-yellow)](https://numpy.org/devdocs/release/1.19.2-notes.html)
[![matplotlib](https://img.shields.io/badge/matplotlib-3.2.0-orange)](https://matplotlib.org/3.2.0/contents.html)
[![scipy](https://img.shields.io/badge/scipy-1.5.2-blue)](https://docs.scipy.org/doc/scipy/release.1.5.2.html)
[![geopy](https://img.shields.io/badge/geopy-2.1.0-red)](https://geopy.readthedocs.io/en/stable/changelog_2xx.html)

## Project structure

* `configuration/` contains configuration parser, default parameters values, configuration files, and logging configuration
  * `config_files/` contains configuration files
      * `config_example.json` an exemplary configuration file, remember that in the file you must use the parameter's stored name, i.e. what is provided as `dest` argument in `parser.add_argument` in `parser.py`
  * `config.py` defines the `Config` class which contains all the simulation parameters and their derivatives and is passed throughout the simulation
  * `logging.py` logging configuration with usage examples
  * `parser.py` the file with a simulation arguments parser, defines every parameter of the simulation, it's default value, type, possible choices etc. Comments here create the best documentation of the simulation parameters
* `electoral_sys/` all logic behind electoral systems, i.e. how to translate votes into seats and winners
  * `electoral_system.py` contains functions for specific electoral systems, vote voting, and changing into election result
  * `seat_assignment.py` contains functions for performing seat assignment within districts (like Jefferson-D'Hondt method)
* `net_generation/` everything necessary to set up a network for the simulation
  * `base.py` contains functions for network generation, initiating states of the nodes, adding zealots etc.
* `plots/` this directory doesn't exist in the repository, but after running the simulation (or a plotting function) it will be created and plots will be generated and saved here by default
* `results/` this directory doesn't exist in the repository, but after running the simulation it will be created and results will be saved here by default
* `scripts/` different scripts for custom tasks, mainly for running `main.py` many times with different parameters
  * `animation.py` a script for making animations of the network showing how states/votes are changing
  * `binom_approx.py` this script requires to run `main.py` manually with the same parameters first, then on top of the results of the simulation plots a binomial approximation, where voters basically flip a coin to chose their state/vote
  * `fit_planar_c.py` a script fitting the `planar_c` parameter value to the commuting data
  * `media_susceptibility.py` this script runs `main.py` for a range of different mass media influence and plots media susceptibility and other measures
  * `media_vs_zealots.py` this script runs `main.py` for a range of different numbers of zealots and different mass media influence and plots the results for cross-influenced system
  * `zealot_susceptibility.py` this script runs `main.py` for a range of different numbers of zealots and plots zealot susceptibility and other measures
* `simulation/` everything to run the dynamical process taking place on the network
  * `base.py` contains functions with the main algorithm of the opinion formation, opinion propagation (social influence), opinion mutation (random noise), and thermalization
* `main.py` the main script for running the whole simulation for a given set of parameters; first thermalizes the system and then runs the process of opinion dynamics performing elections after every given number of steps; saves the results in a `.json` file and plots them (there is an argument `silent` to skip plotting and log less information when using scripts e.g. from `scripts/`)
* `plotting.py` all plotting function
* `tools.py` different useful functions used in various parts of the program

## Examples

### Running a single simulation

Running the simulation with default values:
```bash
$ python3 main.py
```
Running the simulation for a network with 10^4 nodes, average degree equal 20, ratio between probability of connections
within and between the topological communities equal 0.01, one hundred districts (communities), and 5 seats per district:
```bash
$ python3 main.py -n 10000 -avg_deg 20 -ra 0.01 -q 100 -qs 5
```
Running the simulation using the majority rule for state propagation, the probability of random
state update (mutation) equal 0.5, 30 zealots in the network, probability of choosing the zealot state
during mutation equal 0.7 (mass media effect), with no thermalization time at the beginning, and
with results sampled over 10^3 elections:
```bash
$ python3 main.py -p majority -e 0.5 -zn 30 -mm 0.7 -t 0 -s 1000
```
Running the simulation for three districts (communities) of sizes 1000, 700, and 550 nodes, each district with
8, 5, and 4 seats respectively, with an entry threshold equal 5% and 6 political parties (6 possible states),
using Jefferson-D'Hondt seat assignment method:
```bash
$ python3 main.py -q 3 -qn 1000 700 550 -qs 8 5 4 -tr 0.05 -np 6 -qr jefferson
```

### Using a configuration file

To run the last example using a configuration file, a `config.json` file
must be created, containing:
```json
{
    "_comment_": "exemplary configuration",
    "q": 3,
    "district_sizes": [1000, 700, 550],
    "seats": [8, 5, 4],
    "threshold": 0.05,
    "num_parties": 6,
    "seat_rule": "jefferson"
}
```
The names of the parameters must correspond to what is provided as `dest` argument in `parser.add_argument`
in `parser.py`. Other parameters (keys) will be ignored, so you can use a key like `"_comment_"` to add some description of the configuration file.
Then the main script must be executed providing a path to the configuration file:
```bash
$ python3 main.py --config_file <path_to_the_file>/config.json
```
Normally, the simulation will compute results under two electoral systems - one with a single country-wide district
and the other with `q` electoral districts. Both electoral systems will use the same parameters specified in the
basic configuration, i.e. they will have the same `threshold`, `seats`, and `seat_rule` values. It is possible,
however, to test many electoral systems with different details in one simulation run.
An additional parameter `alternative_systems` can be provided (only in a configuration file). It must be a list
of dictionaries, each containing a basic configuration for an alternative electoral system. Then, for each sample
results for two basic and all alternative electoral systems will be computed. Each alternative ES must contain
a `name` and a `type` parameters. The `type` parameter can have two values: `basic` or `merge`. Both types
can specify theirs own `threshold`, `seats`, and `seat_rule` values that will be used instead of those from the
general configuration. The `basic` alternative ES will then use the same districts as specified by `q` (and other
parameters from the basic configuration). The `merge` alternative ES has an additional argument `dist_merging`
which indicates how to merge the basic `q` electoral districts into new (bigger) ones. `dist_merging` must be a list
of a length `q` with ids of new districts - any districts having the same id will be merged into a new one. The list
can also contain just one element - in that case all districts will be merged and a single country-wide district
will be used (with new parameters if specified). An example extending the above configuration file could look like this:
```json
{
    "_comment_": "exemplary configuration",
    "q": 3,
    "district_sizes": [1000, 700, 550],
    "seats": [8, 5, 4],
    "threshold": 0.05,
    "num_parties": 6,
    "seat_rule": "jefferson",
    "alternative_systems": [
      {
        "name": "basic_dist_system",
        "type": "basic",
        "seat_rule": "hare",
        "seats": [10, 5, 4],
        "threshold": 0.1
      },
      {
        "name": "merge_all",
        "type": "merge",
        "seat_rule": "hare",
        "seats": [10, 5, 4],
        "threshold": 0.1,
        "dist_merging": [0]
      },
      {
        "name": "merge_two",
        "type": "merge",
        "seats": [10, 5, 4],
        "dist_merging": [0, 1, 1]
      }
    ]
}
```
Here the `basic_dist_system` would use the same districts as in the main configuration,
with Hare quota seat assignment instead of Jefferson-D'Hondt method, with increased
threshold of 10%, and 2 more seats in the first district. The `merge_all` system would use exactly the same values,
but applied to a single country-wide district (with 2 more seats overall). Using these two alternative systems we
can obtain results that would otherwise require running the simulation twice with different parameters.
Finally, the `merge_two` system will use the basic configuration, but with the first district having 2 more seats,
and the second and third district merged into one (therefore having 9 seats as a new district).

### Running many simulations with scripts

The best way to run the scripts from the `scripts/` directory with a particular configuration is also
by providing a configuration file, which will be then passed to the `main.py` script when it's executed.
This way we can be sure that each simulation uses the same parameters without changing the scripts.
The only thing you might want to adjust is the value of constants at the top of each script, for example
the range of number of zealots to be simulated. Also, **remember not to specify the script-specific
parameters in the configuration file**, as the configuration file has priority over the command-line arguments.
So for `zealot_susceptibility.py`
don't specify the number of zealots in the file, or for `media_susceptibility.py` don't specify
the mass media effect in the file etc. You can ran those scripts as the main file:
```bash
$ python3 zealot_susceptibility.py --config_file <path_to_the_file>/config.json
```
Parameters provided in the command line are not passed to the `main.py` when executed, except
for the configuration file.

## Tests

The program uses python `unittest` module for testing the software.
Tests for the project are collected in `tests/` directories in files named `*_tests.py`.
To run all the tests use:
```bash
$ python3 -m unittest discover -s <repo_directory> -p '*_tests.py'
```

## License

[![scipy](https://img.shields.io/badge/licence-MIT-blue)](https://opensource.org/licenses/MIT)
