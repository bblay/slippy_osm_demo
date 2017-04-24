#
# This file defines the docker image.
# Make sure you run the image with a persistent postgres data folder, e.g
#
#   docker build -t osmgb .
#   docker run -v /data/docker/osmgb:/var/lib/postgresql/data -p 5432:5432 osmgb
#
# On a Mac you'll have to share /data via Docker's preferences on the OS notification bar.
#

FROM postgres:9.6
RUN apt-get update
RUN apt-get install -y wget osm2pgsql

COPY populate_osm.sh /usr/local/bin/
RUN chown postgres:postgres /usr/local/bin/populate_osm.sh
RUN chmod 744 /usr/local/bin/populate_osm.sh

RUN mkdir /data
RUN chown postgres:postgres /data
RUN chmod 744 /data
