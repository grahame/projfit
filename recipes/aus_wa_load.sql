-- figure out boundary of WA
SELECT ST_SimplifyPreserveTopology(ST_Transform(the_geom, 4326), 1) AS geom
    INTO fit_geom
    FROM aust
    WHERE state_name = 'Western Australia';
