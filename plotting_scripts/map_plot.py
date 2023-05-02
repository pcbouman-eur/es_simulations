import os
import sys
import inspect
import folium
from folium import plugins
import random

# path hack for imports to work when running this script from any location,
# without the hack one has to manually edit PYTHONPATH every time
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from configuration.parser import get_arguments
from plotting import COLORS_MANY


BLACK = '#303030'
WHITE = '#ffffff'
GRAY = '#a0a0a0'
# https://gadm.org/
india_geojson = 'plotting_scripts/india.geojson'  # 'https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson'
poland_geojson = 'plotting_scripts/poland.geojson'  # 'https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/wojewodztwa/wojewodztwa-max.geojson'
israel_geojson = 'plotting_scripts/israel.geojson'
TO_PLOT = israel_geojson


def draw_map(config):
    min_lat = min(config.district_coords, key=lambda x: x[0])[0]
    max_lat = max(config.district_coords, key=lambda x: x[0])[0]
    min_lon = min(config.district_coords, key=lambda x: x[1])[1]
    max_lon = max(config.district_coords, key=lambda x: x[1])[1]

    m = folium.Map(tiles=None, zoom_start=5.5, max_bounds=True,  # cartodbpositron stamenwatercolor
                   location=[(min_lat+max_lat)/2, (min_lon+max_lon)/2])

    style = {'fillColor': GRAY, 'color': BLACK}
    folium.GeoJson(TO_PLOT, name="geojson", style_function=lambda x: style).add_to(m)

    colors = COLORS_MANY.copy()
    random.seed(44)
    random.shuffle(colors)

    for i, (lat, lon) in enumerate(config.district_coords):
        color = colors[i % len(colors)]
        icon = folium.plugins.BeautifyIcon(background_color=color, icon='circle', border_width=2,
                                           border_color=BLACK, text_color=WHITE,
                                           icon_shape='marker')
        # icon = folium.Icon(color=BLACK, icon_color=WHITE, icon='circle', prefix='fa')
        folium.Marker([lat, lon], icon=icon).add_to(m)

    html_to_insert = "<style>.leaflet-container {background: #fff !important;}</style>"
    m.get_root().header.add_child(folium.Element(html_to_insert))

    m.fit_bounds((max_lat, max_lon), (min_lat, min_lon))

    m.save(f'plots/{cfg.config_file.split("/")[-1].replace(".json", ".html")}')


if __name__ == '__main__':
    os.chdir(parentdir)
    cfg = get_arguments()
    draw_map(cfg)



