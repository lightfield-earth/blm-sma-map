# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "geopandas==1.0.1",
#     "leafmap[maplibre]==0.43.11",
#     "marimo",
# ]
# ///

import marimo

__generated_with = "0.23.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import json
    import leafmap.maplibregl as leafmap
    from leafmap.maplibregl import Layer

    return Layer, json, leafmap


@app.cell
def _(Layer, json, leafmap):
    with open('basemap_style_spec.json', 'r') as f:
        style_spec = json.load(f)

    m = leafmap.Map(
        center=(-98.5795,39.8283),  # Center of the US
        zoom=3,                     # Initial zoom level
        min_zoom=2,
        max_zoom=9,
        height='600px',                            
        style=style_spec,
        use_message_queue=True,     # Needed to export HTML
        hash=True,
        controls={
            "geolocate": "top-right",
            "navigation": "top-right",
            "fullscreen": "top-right", 
            "scale": "bottom-left"
        }
    )

    # Link to BLM national surface management agency data on AWS S3
    blm_sma_source = {
        'type' : 'vector',
        'tiles' : ['https://tiles.lightfield.ag/blm_national_surface_management_data_z9_D11/{z}/{x}/{y}.mvt'],
        'minzoom' : 2,
        'maxzoom' : 9
    }
    m.add_source('blm-sma-source', blm_sma_source)

    # Define the paint property
    paint = {
        'fill-color': [
            'case',
            ['==', ['get', 'ADMIN_DEPT_CODE'], 'PVT'], 'hsl(5, 91%, 83%)',
            ['in', ['get', 'ADMIN_DEPT_CODE'], ['literal', ['ST', 'LG']]], 'hsl(286, 32%, 85%)',
            ['==', ['get', 'ADMIN_DEPT_CODE'], 'DOD'], 'hsl(208, 46%, 80%)',
            ['==', ['get', 'ADMIN_DEPT_CODE'], 'DOE'], 'hsl(60, 100%, 90%)',
            ['all', ['==', ['get', 'ADMIN_DEPT_CODE'], 'DOI'], ['==', ['get', 'ADMIN_AGENCY_CODE'], 'BIA']], 'hsl(35, 98%, 82%)',
            ['==', ['get', 'ADMIN_DEPT_CODE'], 'DOI'], 'hsl(41, 43%, 82%)',
            ['==', ['get', 'ADMIN_DEPT_CODE'], 'USDA'], 'hsl(109, 49%, 85%)',
            ['in', ['get', 'ADMIN_DEPT_CODE'], ['literal', ['OTHFE', 'DOS', 'DOT', 'VA', 'DHS', 'HHS', 'HUD', 'IA', 'DOC', 'DOJ']]], 'hsl(329, 90%, 92%)',
            ['in', ['get', 'ADMIN_DEPT_CODE'], ['literal', ['NVTALL', 'NVTPIC']]], 'hsl(35, 98%, 82%)',
            'hsl(332, 0%, 90%)'  # Default color for all other cases
        ]
    }

    # Add the BLM SMA vector tile layer
    blm_layer = Layer(
        id='blm-sma-polygons',
        type='fill',
        source='blm-sma-source',
        source_layer='blm_national_surface_management_data',
        paint=paint
    )
    m.add_layer(blm_layer, before_id='Residential')

    # Add the Copernicus GLO-30 hillshade raster tile layer
    # Recall that due to the variable opacity within this layer, blending with the underlying
    # data layer results naturally, as long as this layer is placed on top of the data layer.
    m.add_tile_layer(
        url="https://tiles.lightfield.ag/hillshade_tiles_planet_z12_webp/{z}/{x}/{y}.webp",
        before_id='Residential',
        paint={
            "raster-fade-duration": 0,       # Remove default 300 ms fade duration
            "raster-resampling": "nearest",  # Use nearest neighbor instead of linear
        }
    )

    image = "LightField Logo.png"
    m.add_image(image=image, position="bottom-left", height='50px')

    legend_dict = {
        'Private': 'f6b0a9',
        'State / Local': 'decae1',
        'Dept of Defense': 'b9cce1',
        'Dept of Energy': 'fefed0',
        'Tribal': 'f8daaa',
        'Dept of Interior': 'e2d9c0',
        'Dept of Agriculture': 'd2e9c9',
        'Other Federal': 'f6daea',
        'Undetermined': 'e4e4e4'
    }
    m.add_legend('Land Management',legend_dict=legend_dict, position="top-left")

    #m.add_globe_control(position="top-right")

    m
    return (m,)


@app.cell
def _(m):
    m.to_html('index_stage.html',title='BLM Surface Management Agency Layer',overwrite=True)
    return


if __name__ == "__main__":
    app.run()
