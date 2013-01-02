#!/bin/bash

# load in electorate boundaries
(
    cd data && 
    (
        if [ ! -f 1259030001_ste11aaust_shape.zip ]; then
            wget 'http://www.ausstats.abs.gov.au/ausstats/subscriber.nsf/0/D39E28B23F39F498CA2578CC00120E25/$File/1259030001_ste11aaust_shape.zip'
            unzip 1259030001_ste11aaust_shape.zip
        fi
        shp2pgsql -s 4283 -I STE11aAust.shp aust | psql projfit
    )
)
