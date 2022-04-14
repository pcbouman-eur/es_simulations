"""
A script running the simulation for a given configuration (you can provide a config file),
saving plots of the graph on the way, and creating an animation at the end.
This script doesn't have many options as it is meant to play around with it,
so if you want to get some fancy plots etc. just modify the code.
"""
import os
import sys
import glob
import inspect

# path hack for imports to work when running this script from any location,
# without the hack one has to manually edit PYTHONPATH every time
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from configuration.parser import get_arguments
from configuration.logging import log
from tools import run_with_time, compute_edge_ratio
from plotting import plot_traj, plot_network
from net_generation.base import init_graph, add_zealots
from simulation.base import run_simulation, run_thermalization


NUM_FRAMES = 100  # the number of frames to save
MC_STEP = 10  # the number of Monte Carlo steps of simulation between frames


@run_with_time
def make_animation(config):
    os.makedirs('plots/animation', exist_ok=True)
    os.chdir('plots/animation')

    # initialize the graph
    graph = init_graph(config.n, config.district_sizes, config.avg_deg, block_coords=config.district_coords,
                        ratio=config.ratio, planar_const=config.planar_c, euclidean=config.euclidean,
                        state_generator=config.initialize_states, random_dist=config.random_dist,
                        initial_state=config.not_zealot_state, all_states=config.all_states)
    graph = add_zealots(graph, config.n_zealots, zealot_state=config.zealot_state, **config.zealots_config)

    link_fraction, link_ratio = compute_edge_ratio(graph)
    log.info(f'There is {str(round(100.0 * link_fraction, 1))}% of inter-district connections')
    log.info(f'Ratio of inter- to intra-district links is equal {str(round(link_ratio, 3))}')

    # save the layout to use the same one in each frame
    ll = graph.layout()

    # show the first plot with colored districts so one can stop the script and rerun it, if the layout is not nice
    plot_network(graph, config, mode='districts', ig_layout=ll)

    if config.therm_time > 1:
        graph, trajectory = run_thermalization(config, graph, config.epsilon, config.therm_time, n=config.n)
        plot_traj(trajectory, config.suffix)
    plot_network(graph, config, mode='states', ig_layout=ll, save_as=f'{0:05d}.png')

    for i in range(NUM_FRAMES):
        log.info(f'Running loop no. {i}')
        graph = run_simulation(config, graph, config.epsilon, MC_STEP * config.n, n=config.n)
        plot_network(graph, config, mode='states', ig_layout=ll, save_as=f'{i + 1:05d}.png')

    # change the command in this line to create the animation with your preferred program and in the preferred format
    # for example, you might also use 'convert -delay 10 -loop 0 %05d.png animation.gif' etc.
    os.system('ffmpeg -framerate 10 -i %05d.png animation.mp4')

    # don't remove .png files if you want to be able to play around
    # with animation parameters (like speed) without having to run the whole simulation again
    response = input('Do you want to remove the created .png files? [Y/N] ')
    if response == 'Y':
        log.info(f'Removing the .png files')
        for f in glob.glob('[0-9]' * 5 + '.png'):
            os.remove(f)


if __name__ == '__main__':
    os.chdir(parentdir)
    cfg = get_arguments()
    make_animation(cfg)
