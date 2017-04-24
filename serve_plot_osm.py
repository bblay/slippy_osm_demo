import os

import psycopg2
from bottle import route, run, template
from psycopg2._psycopg import ProgrammingError

from postgis_queries import get_osm_geoms, point_geom_to_html, poly_geom_to_html

@route('/plot_osm/<ids>')
def plot_osm(ids):

    osm_ids = filter(lambda x: x is not None, ids.split(','))

    pg_con = psycopg2.connect(database='osmgb', user='postgres', password=None, host='0.0.0.0')
    pg_cursor = pg_con.cursor()

    try:
        points, polys = get_osm_geoms(pg_cursor, osm_ids)
    except ProgrammingError as err:
        markers_html = ''
        polys_html = ''
        message ='ERROR {}'.format(err)
    else:
        markers_html = point_geom_to_html(points)
        polys_html = poly_geom_to_html(polys)
        message = ''

    return template('plot_osm', ids=osm_ids, message=message, markers=markers_html, polys=polys_html)


if os.uname()[0] == 'Darwin':
    run(host='localhost', port=8080)
else:
    run(host='0.0.0.0', port=8080)
