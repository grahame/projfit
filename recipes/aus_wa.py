
# recipe parameters
config = {
    "prefix": "western_australia_",
    "title": "Western Australia",
    "tests": { 
        3112 : "GDA94 / Geoscience Australia Lambert",
        3577 : "GDA94 / Australian Albers",
        32750 : "WGS84 / UTM zone 50S",
        32751 : "WGS84 / UTM zone 51S",
        32752 : "WGS84 / UTM zone 52S",
    }
}

def load_geometry():
    run_cmd("recipes/aus_wa_load.sh")
    run_sql_from("recipes/aus_wa_load.sql")

