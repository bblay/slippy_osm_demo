"""
This script is used to check we can access the postgis database inside the Docker container.

To find the docker container's ip: (On my Mac this was 0.0.0.0)
    docker inspect <container_name> | grep HostIp

To run this script:
    python check.py 0.0.0.0

Or you can connect your psql to the container:
    psql -h 0.0.0.0 -U postgres

"""

import argparse

import psycopg2

from postgis_queries import get_osm_geom


# ids = [-175342, -57516, 15732153, 32062097]
ids = [-57516, 32062097]

def check_db(host):
    print 'getting cursor'
    pg_con = psycopg2.connect(database='osmgb', user='postgres', password=None, host=host)
    pg_cursor = pg_con.cursor()
    for osm_id in ids:
        print osm_id
        try:
            geom = get_osm_geom(pg_cursor, osm_id, simplify=False)
            print 'got geo for osm id', osm_id
        except KeyboardInterrupt as err:
            break
        except Exception as err:
            print 'failed to get geom for osm id', osm_id, err


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--host', default='0.0.0.0')
    args = arg_parser.parse_args()

    check_db(args.host)
