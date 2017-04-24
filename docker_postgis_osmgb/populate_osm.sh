#!/usr/bin/env bash

#
# This script populates the database with OSM data for Great Britain.
# Run this once to populate the database, e.g
#
#   docker exec <container_name> su postgres -c populate_osm.sh
#
# You can find <container_name> via "docker ps", they look like "unruffled_babbage".
#

echo "downloading osm data for GB"
cd /data
wget http://download.geofabrik.de/europe/great-britain-latest.osm.bz2
cd -

echo "populating, indexing and clustering postgres - this will take hours"
psql -c "drop database if exists osmgb;"
psql -c "create database osmgb;"
psql -d osmgb -c "CREATE EXTENSION postgis;"
psql -d osmgb -c "CREATE EXTENSION hstore;"

osm2pgsql --create --database osmgb --latlong --number-processes 2 --multi-geometry --slim --drop --cache 5000 /data/great-britain-latest.osm.bz2

psql -d osmgb -c "create INDEX polygon_way_index ON planet_osm_polygon USING GIST (way);"
psql -d osmgb -c "cluster planet_osm_polygon using polygon_way_index;"
rm /data/great-britain-latest.osm.bz2
