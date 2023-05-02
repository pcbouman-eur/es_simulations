import os
import sys
import inspect
import random

# path hack for imports to work when running this script from any location,
# without the hack one has to manually edit PYTHONPATH every time
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from configuration.parser import get_arguments
from net_generation.base import init_graph
from plotting import COLORS_MANY, plot_network


BLACK = '#303030'
WHITE = '#ffffff'
GRAY = '#a0a0a0'


def draw_net(config):
    colors = COLORS_MANY.copy()
    random.seed(42)
    random.shuffle(colors)

    graph = init_graph(config.n, config.district_sizes, config.avg_deg, block_coords=config.district_coords,
                       ratio=config.ratio, planar_const=config.planar_c, euclidean=config.euclidean,
                       state_generator=config.initialize_states, random_dist=config.random_dist,
                       initial_state=config.not_zealot_state, all_states=config.all_states)

    save_as = f'plots/{cfg.config_file.split("/")[-1].replace(".json", "_net.png")}'
    plot_network(graph, config, mode='districts', layout='geo_strict', save_as=save_as, node_size=8, std=0.0002, colors=colors)


if __name__ == '__main__':
    os.chdir(parentdir)
    cfg = get_arguments()
    draw_net(cfg)



