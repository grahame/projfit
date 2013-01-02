
# recipe parameters
config = {
    "prefix": "australia_",
    "title": "Australia",
    "tests": { 
        3112 : "GDA94 / Geoscience Australia Lambert",
        3577 : "GDA94 / Australian Albers",
    }
}

def load_geometry():
    run_cmd("recipes/aus_load.sh")
    run_sql_from("recipes/aus_load.sql")

