#!/usr/bin/env python

import sys, os, csv, imp, subprocess, psycopg2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt, sys, csv
from mpl_toolkits.basemap import Basemap
from matplotlib import cm
import numpy as np

matplotlib.rcParams.update({'font.size': 5})

if __name__ == '__main__':
    def plot_results():
        srid_results = { }
        c_id = None
        lngs = []
        lats = []
        for row_id,srid,lng,lat,e in get_rows("SELECT id, srid, lng, lat, avg_per_error FROM results ORDER BY id;"):
            if not srid_results.has_key(srid):
                srid_results[srid] = []
            srid_results[srid].append(e)
            if c_id != row_id:
                lngs.append(lng)
                lats.append(lat)
                c_id = row_id
        proj_lat1, proj_lat2 = lat2+0.5, lat1-0.5
        proj_lng1, proj_lng2 = lng1-0.5, lng2+0.5

        # common colour scheme so images are comparable
        vmin = min([min(t) for t in srid_results.values()])
        vmax = max([max(t) for t in srid_results.values()])

        for idx, (srid, title) in enumerate(loader.config['tests'].viewitems()):
            vals = srid_results[srid]
            fig = plt.figure()
            plt.figure(idx+1)
            plt.title('ST_Distance vs. ST_Distance_Spheroid(WGS84)\n%s' % (title))
            m = Basemap(projection='lcc',
                    lat_0=proj_lat1+(proj_lat2-proj_lat1)/2.,
                    lon_0=proj_lng1+(proj_lng2-proj_lng1)/2.,
                    llcrnrlon=proj_lng1, llcrnrlat=proj_lat2,
                    urcrnrlon=proj_lng2, urcrnrlat=proj_lat1)
            x, y = m(lngs, lats)
            m.scatter(x, y, vmin=vmin, vmax=vmax, s=3, marker='s', edgecolor='none', c=vals, cmap=cm.OrRd)
            plt.xlabel("Average error %.2f%%, median error %.2f%%, std dev %.2f" % (np.average(vals), np.median(vals), np.std(vals)))
            cbar = plt.colorbar()
            cbar.set_label("% error (four nearest points)")
            fig.savefig('plots/%s%s.png' % (loader.config['prefix'], srid), dpi=200)
    def run_sql(sql):
        cmd = subprocess.Popen(["psql", "projfit"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        cmd.stdin.write(sql)
        cmd.stdin.close()
        rv = cmd.stdout.read()
        cmd.stdout.close()
        cmd.wait()
        return rv
    def run_sql_from(path):
        with open(path) as fd:
            sql = fd.read()
        return run_sql(sql)
    def get_rows(sql):
        conn = psycopg2.connect("dbname=projfit")
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        return rows
    def gen_points(fname):
        p = 100
        lat_inc = (lat2 - lat1) / (p + 2)
        lng_inc = (lng2 - lng1) / (p + 2)
        def latlng(x, y):
            return 'POINT(%f %f)' % (lng1 + lng_inc * y, lat1 + lat_inc * x)
        with open(fname, "w") as fd:
            writer = csv.writer(fd)
            writer.writerow(["id", "pt", "n", "s", "e", "w"])
            c = 1
            for x in xrange(1, p+1):
                for y in xrange(1, p+1):
                    pt = latlng(x, y)
                    n = latlng(x, y+1)
                    s = latlng(x, y-1)
                    e = latlng(x+1, y)
                    w = latlng(x-1, y)
                    writer.writerow([c, pt, n, s, e, w])
                    c += 1
    def run_cmd(*args):
        rv = subprocess.call(args)
        if rv != 0:
            raise Exception("cmd `%s' failed" % script)

    recipe = sys.argv[1]
    loader = imp.load_source('_plugin', recipe)
    loader.run_sql = run_sql
    loader.run_sql_from = run_sql_from
    loader.run_cmd = run_cmd

    # rebuild database
    run_cmd("dropdb", "projfit")
    run_cmd("./mkdb.sh", "projfit")
    loader.load_geometry()
    # figure out bounding box of the resulting geometry
    lng1, lng2, lat1, lat2 = get_rows("SELECT ST_Xmin(bbox), ST_Xmax(bbox), ST_Ymin(bbox), ST_Ymax(bbox) from (SELECT ST_Envelope(geom) as bbox FROM fit_geom) as sub1")[0]
    # generate a spray of points over the geometry
    points_file = "%s/tmp/wa_points.csv" % (os.getcwd())
    gen_points(points_file)
    run_sql("""
CREATE TABLE load_points (id integer, point text, n text, s text, e text, w text);
COPY load_points FROM '%s' CSV HEADER;

-- load in our WGS84 test points
SELECT
    id,
    st_setsrid(st_geomfromtext(point), 4326) as point,
    st_setsrid(st_geomfromtext(n), 4326) as n,
    st_setsrid(st_geomfromtext(s), 4326) as s,
    st_setsrid(st_geomfromtext(e), 4326) as e,
    st_setsrid(st_geomfromtext(w), 4326) as w
    INTO all_points
    FROM load_points;
DROP TABLE load_points;
CREATE INDEX all_points_gist ON all_points USING gist(point);

-- chop down to points within the geometry
SELECT id, point, n, s, e, w                                                                       
    INTO points
    FROM all_points
    WHERE st_contains((SELECT geom from fit_geom), point);
DROP TABLE all_points;
CREATE INDEX points_gist ON points USING gist(point);

-- get the 'true' distances
SELECT
    id,
    point,
    ST_Distance_Spheroid(point, n, 'SPHEROID["WGS 84",6378137,298.257223563]') AS true_dn,
    ST_Distance_Spheroid(point, s, 'SPHEROID["WGS 84",6378137,298.257223563]') AS true_ds,
    ST_Distance_Spheroid(point, e, 'SPHEROID["WGS 84",6378137,298.257223563]') AS true_de,
    ST_Distance_Spheroid(point, w, 'SPHEROID["WGS 84",6378137,298.257223563]') AS true_dw
    INTO true_distances
    FROM points;

-- table for our tests on each SRID
CREATE TABLE srid_distances
    (id integer, srid integer, dn numeric, ds numeric, de numeric, dw numeric);
""" % (points_file))
    # run the SRID experiments
    for srid, title in loader.config['tests'].viewitems():
        run_sql("""
INSERT INTO srid_distances (id, srid, dn, ds, de, dw)
    SELECT
        id,
        {0},
        ST_Distance(ST_Transform(point, {0}), ST_Transform(n, {0})) AS dn,
        ST_Distance(ST_Transform(point, {0}), ST_Transform(s, {0})) AS ds,
        ST_Distance(ST_Transform(point, {0}), ST_Transform(e, {0})) AS de,
        ST_Distance(ST_Transform(point, {0}), ST_Transform(w, {0})) AS dw
        FROM points
        """.format(srid))
    # calculate the average errors from 'true' distances
    run_sql("""
SELECT
    true_distances.id,
    srid,
    st_x(point) as lng,
    st_y(point) as lat,
    (abs(true_dn - dn)/true_dn + 
        abs(true_ds - ds)/true_ds + 
        abs(true_de - de)/true_de + 
        abs(true_dw - dw)/true_dw)/4*100 AS avg_per_error
    INTO results
    FROM srid_distances
    INNER JOIN true_distances ON true_distances.id = srid_distances.id;
    """)

    plot_results()

