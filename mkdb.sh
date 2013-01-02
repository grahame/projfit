#!/bin/bash

createdb "$1"
psql "$1" -f /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql
psql "$1" -f /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql

