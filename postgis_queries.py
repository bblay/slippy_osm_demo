import ujson

GEOJSON_SELECT = 'ST_AsGeoJSON(way)'
# 0.001 degrees is roughly about 100m
GEOJSON_SIMPLIFY_SELECT = 'ST_AsGeoJSON(ST_SimplifyPreserveTopology(way, 0.001))'


def run_query(pg_cursor, query):
    """
    Run a PostGIS query and format the rows into dicts.

    :param pg_cursor:
    :param str query:
    :rtype: list[dict]
    :return: A list of row dicts.

    """
    pg_cursor.execute(query)
    rows = pg_cursor.fetchall()
    result = []
    column_names = [column.name for column in pg_cursor.description]
    for row in rows:
        result.append({column_name: value for column_name, value in zip(column_names, row)})
    return result


def get_osm_geom(pg_cursor, osm_id, simplify=True):
    """
    Get the GeoJSON geometry for a given OSM id.

    :param pg_cursor:
    :param int osm_id:
    :param bool simplify: Whether to use ST_SimplifyPreserveTopology (with tolerance 0.001) on the geom.
    :rtype: str
    :return: The GeoJSON geometry.

    """
    geojson_select = GEOJSON_SIMPLIFY_SELECT if simplify else GEOJSON_SELECT

    query = "select {geojson_select} from planet_osm_polygon where osm_id = {osm_id};".format(
        geojson_select=geojson_select, osm_id=osm_id)
    geom = run_query(pg_cursor, query)

    if not geom:
        query = "select {geojson_select} from planet_osm_point where osm_id = {osm_id};".format(
            geojson_select=geojson_select, osm_id=osm_id)
        geom = run_query(pg_cursor, query)

    return geom


def get_osm_geoms(pg_cursor, osm_ids, simplify=True):
    """
    Get the GeoJSON geometries for a given list of OSM ids.

    :param pg_cursor:
    :param list[int] osm_ids: The OSM ids for which to get geoms.
    :param bool simplify: Whether to use ST_SimplifyPreserveTopology (with tolerance 0.001) on the geom.
    :rtype: list[str]
    :return: A list of GeoJSON geometries.

    """
    geojson_select = GEOJSON_SIMPLIFY_SELECT if simplify else GEOJSON_SELECT

    points = {}
    polys = {}

    for osm_id in osm_ids:
        query = "select {geojson_select} from planet_osm_polygon where osm_id = {osm_id};".format(
            geojson_select=geojson_select, osm_id=osm_id)
        geom = run_query(pg_cursor, query)

        geom_size = 0
        for ujson_dict in geom:
            for v in ujson_dict.itervalues():
                geom_size += len(v)
        print 'geom size', geom_size

        if geom:
            polys[osm_id] = geom
        else:
            query = "select {geojson_select} from planet_osm_point where osm_id = {osm_id};".format(
                geojson_select=geojson_select, osm_id=osm_id)
            geom = run_query(pg_cursor, query)
            if geom:
                points[osm_id] = geom
            else:
                raise ValueError("osm_id {} geom not found".format(osm_id))

    return points, polys


def make_poly_str(poly_with_holes):
    ring_strs = []
    for ring in poly_with_holes:

        latlon_strs = []
        for lon, lat in ring:
            latlon_str = '[{lat}, {lon}]'.format(lat=lat, lon=lon)
            latlon_strs.append(latlon_str)

        ring_str = ', '.join(latlon_strs)
        ring_strs.append('\n        [\n            {}\n        ]'.format(ring_str))

    poly_str = ', '.join(ring_strs)

    poly_str = '\n    [\n        {}\n    ]'.format(poly_str)
    return poly_str


def point_geom_to_html(points):
    """
    E.g "var marker = L.marker([51.5, -0.09]).addTo(mymap);"

    """
    lines = []
    for id, point in points.iteritems():
        assert len(point) == 1
        point_str = point[0]['st_asgeojson']
        point_dict = ujson.loads(point_str)
        lon, lat = point_dict['coordinates']
        lines.append("var marker = L.marker([{lat}, {lon}]).addTo(mymap);".format(lat=lat, lon=lon))

    return '\n'.join(lines)


def poly_geom_to_html(polys):
    """
    E.g "var polygon = L.polygon([[51.509, -0.08], [51.503, -0.06], [51.51, -0.047]]).addTo(mymap);"

    """
    lines = []
    for id, poly in polys.iteritems():
        assert len(poly) == 1  # should fail for multi-polys, deal with it later
        poly_str = poly[0]['st_asgeojson']
        poly_dict = ujson.loads(poly_str)

        if poly_dict['type'] == 'Polygon':
            geom_str = make_poly_str(poly_dict['coordinates'])
        elif poly_dict['type'] == 'MultiPolygon':
            poly_strs = []
            for poly_with_holes in poly_dict['coordinates']:
                poly_strs.append(make_poly_str(poly_with_holes))
            geom_str = '\n[\n{}\n]'.format(', '.join(poly_strs))
        else:
            raise ValueError()

        lines.append("var poly = L.polygon([{geom_str}]).addTo(mymap);".format(geom_str=geom_str))

    return '\n'.join(lines)
