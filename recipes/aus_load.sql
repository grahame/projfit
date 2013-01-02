-- figure out boundary of Australia
SELECT ST_Buffer(ST_SimplifyPreserveTopology(st_collect(st_transform(the_geom, 4326)), 1), 0) AS geom
    INTO fit_geom
    FROM aust;
