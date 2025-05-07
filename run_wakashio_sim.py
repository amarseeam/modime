import os
import datetime
import gnome.scripting as gs
from gnome.utilities.projections import GeoProjection
import sys
lon = float(sys.argv[2])  # Note: sys.argv[2] is lon, [1] is lat
lat = float(sys.argv[1])
start_position = (lon, lat)
end_position = (lon + 0.001, lat + 0.001)


gs.set_verbose()

# Set base directory for public-facing output
PUBLIC_DIR = '/graphs'
MAPFILE = os.path.join(PUBLIC_DIR, 'mauritius.bna')
IMAGES_DIR = os.path.join(PUBLIC_DIR, 'images')
OIL_FILE = os.path.join(PUBLIC_DIR, 'vlsfo-im-5-imaros_AD02592.json')
NETCDF_FILE = os.path.join(PUBLIC_DIR, 'wakashio_output.nc')
KMZ_FILE = os.path.join(PUBLIC_DIR, 'wakashio_output.kmz')

def make_model(images_dir=IMAGES_DIR):
    print("Creating the map...")
    gnome_map = gs.MapFromBNA(MAPFILE, refloat_halflife=1, raster_size=2048 * 2048)

    renderer = gs.Renderer(
        MAPFILE,
        images_dir,
        image_size=(800, 800),
        viewport=((57.193881, -20.616082),  # bottom-left
                  (57.193881, -19.8997),    # top-left
                  (57.987393, -19.8997),    # top-right
                  (57.987393, -20.616082)), # bottom-right
        projection_class=GeoProjection
    )

    print("Initializing the model...")
    start_time = datetime.datetime(2020, 8, 6, 6, 30)
    model = gs.Model(
        time_step=gs.hours(6),
        start_time=start_time,
        duration=gs.days(18),
        map=gnome_map,
        uncertain=True
    )

    print("Adding outputters...")
    gs.remove_netcdf(NETCDF_FILE)
    model.outputters += renderer
    model.outputters += gs.NetCDFOutput(NETCDF_FILE, which_data='all')
    model.outputters += gs.KMZOutput(KMZ_FILE, output_timestep=gs.days(1))

    print("Adding movers...")
    model.movers += gs.RandomMover(diffusion_coef=100000)

    wind = gs.Wind(
    timeseries=[
        (start_time + gs.days(0), (5.46, 137.7)),
        (start_time + gs.days(1), (7.96, 140.8)),
        (start_time + gs.days(2), (8.12, 142.9)),
        (start_time + gs.days(3), (8.75, 122.9)),
        (start_time + gs.days(4), (5.67, 104.0)),
        (start_time + gs.days(5), (5.07, 107.6)),
        (start_time + gs.days(6), (4.74, 95.6)),
        (start_time + gs.days(7), (2.6, 115.2)),
        (start_time + gs.days(8), (7.63, 161.9)),
        (start_time + gs.days(9), (5.37, 100.7)),
        (start_time + gs.days(10), (2.75, 143.2)),
        (start_time + gs.days(11), (4.31, 131.0)),
        (start_time + gs.days(12), (5.29, 90.4)),
        (start_time + gs.days(13), (3.39, 91.3)),
        (start_time + gs.days(14), (5.86, 124.0)),
        (start_time + gs.days(15), (7.61, 88.5)),
        (start_time + gs.days(16), (5.95, 82.7)),
        (start_time + gs.days(17), (6.99, 92.7))
    ],
    units='m/s',
    extrapolation_is_allowed=True
)

    model.movers += gs.WindMover(wind)

    print("Adding a spill with oil data from ADIOS database...")
#    start_position = (57.744631, -20.438119)
#    end_position = (57.745631, -20.437119)
    print(f"Start Position: {start_position}")
    print(f"End Position: {end_position}")
    try:
        oil = gs.GnomeOil(filename=OIL_FILE)
    except:
        oil = gs.nonweathering_substance()

    model.spills += gs.surface_point_line_spill(
        num_elements=10000,
        start_position=start_position,
        end_position=end_position,
        release_time=start_time,
        end_release_time=start_time + gs.days(10),
        amount=1000,
        substance=oil,
        units='tons',
        windage_range=(0.03, 0.03),
        windage_persist=-1,
        name='Wakashio spill - main'
    )

    model.spills += gs.surface_point_line_spill(
        num_elements=1000,
        start_position=start_position,
        end_position=end_position,
        release_time=start_time + gs.days(10),
        end_release_time=start_time + gs.days(16),
        amount=50,
        substance=oil,
        units='tons',
        windage_range=(0.03, 0.03),
        windage_persist=-1,
        name='Wakashio spill - residual'
    )

    model.environment += gs.Water()
    return model

if __name__ == "__main__":
    os.makedirs(IMAGES_DIR, exist_ok=True)
    print("Setting up the model...")
    model = make_model()
    print("Running the model...")
    model.full_run()
    print(f"Simulation complete. Results saved in '{IMAGES_DIR}'")
