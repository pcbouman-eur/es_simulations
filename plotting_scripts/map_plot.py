import folium
from folium import plugins
import random

from configuration.parser import get_arguments
from plotting import COLORS_MANY


BLACK = '#303030'
GRAY = '#808080'
# https://gadm.org/
india_geojson = 'https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson'
poland_geojson = 'https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/wojewodztwa/wojewodztwa-max.geojson'
israel_geojson = 'israel.geojson'


def draw_map(config):
    min_lat = min(config.district_coords, key=lambda x: x[0])[0]
    max_lat = max(config.district_coords, key=lambda x: x[0])[0]
    min_lon = min(config.district_coords, key=lambda x: x[1])[1]
    max_lon = max(config.district_coords, key=lambda x: x[1])[1]

    m = folium.Map(tiles=None, zoom_start=5.5, max_bounds=True,  # cartodbpositron stamenwatercolor
                   location=[(min_lat+max_lat)/2, (min_lon+max_lon)/2])

    style = {'fillColor': GRAY, 'color': BLACK}
    folium.GeoJson(israel_geojson, name="geojson", style_function=lambda x: style).add_to(m)

    for i, (lat, lon) in enumerate(config.district_coords):
        color = random.choice(COLORS_MANY)
        icon = folium.plugins.BeautifyIcon(background_color=color, icon='circle', border_width=2,
                                           border_color=BLACK, text_color='#ffffff',
                                           icon_shape='marker')
        # icon = folium.Icon(color=BLACK, icon_color=WHITE, icon='circle', prefix='fa')
        folium.Marker([lat, lon], icon=icon).add_to(m)

    m.fit_bounds((max_lat, max_lon), (min_lat, min_lon))

    m.save('map.html')


if __name__ == '__main__':
    cfg = get_arguments()
    draw_map(cfg)



