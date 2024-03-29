
See the file `LICENSE` for software license details.

Measures how well an `ST_Distance` calculation is matching the
slower (but more correct) measurement of distance using
`ST_Distance_Spheroid` on the WGS 84 spheroid. Example plot below,
from running the `aus` recipe.

![Example fit to Australia](https://raw.github.com/grahame/projfit/master/examples/australia_3112.png "Geoscience Australia Lambert fit")

![Example fit to Western Australia](https://raw.github.com/grahame/projfit/master/examples/western_australia_32750.png "UTM zone 50S fit")

Requirements:

 - Postgresql / PostGIS
 - Python, Matplotlib, Basemap
 - GEOS, GDAL

Usage:

    ./projfit.py recipes/aus.py
    ./projfit.py recipes/aus_wa.py

Graphs are output into the plots/ directory. Always run projfit.py from 
the checkout root.

To write your own recipes, copy the pattern. In brief, you specify the 
tests to run in the config global at the top of your recipe, and you 
must provide a `load_geometry` method, at the conclusion of which there 
will be a table in the database called `fit_geom` with one row and one 
column, `geom` containing the geometry the experiments are to be applied to.

This is a quick hack -- but I couldn't find anything else doing what 
I wanted. Patches to clean this up (and maybe use SQLalchemy rather than 
fragments of shell and raw SQL) would be gladly accepted.



