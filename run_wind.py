import os
import sys
import datetime
import requests
import gnome.scripting as gs
from gnome.utilities.projections import GeoProjection

# Extract lat/lon from command line args
lat = float(sys.argv[1])
lon = float(sys.argv[2])
start_position = (lon, lat)

gs.set_verbose()

# Paths
PUBLIC_DIR = '/graphs'
MAPFILE = os.path.join(PUBLIC_DIR, 'mauritius.bna')
IMAGES_DIR = os.path.join(PUBLIC_DIR, 'images')
OIL_FILE = os.path.join(PUBLIC_DIR, 'vlsfo-im-5-imaros_AD02592.json')
NETCDF_FILE = os.path.join(PUBLIC_DIR, 'wakashio_output.nc')
KMZ_FILE = os.path.join(PUBLIC_DIR, 'wakashio_output.kmz')

def fetch_wind_timeseries(lat, lon, start_time):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "wind_speed_10m,wind_direction_10m",
        "timezone": "Indian/Mauritius"
    }
    response = requests.get(url, params=params)
    data = response.json()

    hourly = data['hourly']
    times = hourly['time']
    speeds = hourly['wind_speed_10m']
    dirs = hourly['wind_direction_10m']

    # Average hourly into daily values
    daily = {}
    for t, s, d in zip(times, speeds, dirs):
        date = t[:10]
        if date not in daily:
            daily[date] = {'speeds': [], 'dirs': []}
        daily[date]['speeds'].append(s / 3.6)  # km/h to m/s
        daily[date]['dirs'].append(d)

    timeseries = []
    for i, (date, vals) in enumerate(sorted(daily.items())[:7]):
        avg_speed = sum(vals['speeds']) / len(vals['speeds'])
        avg_dir = sum(vals['dirs']) / len(vals['dirs'])
        timeseries.append((start_time + gs.days(i), (round(avg_speed, 2), round(avg_dir, 1))))

    return timeseries

def make_model(images_dir=IMAGES_DIR):
    print("Creating the map...")
    gnome_map = gs.MapFromBNA(MAPFILE, refloat_halflife=1, raster_size=2048 * 2048)

    renderer = gs.Renderer(
        MAPFILE,
        images_dir,
        image_size=(800, 800),
        viewport=((57.193881, -20.616082),
                  (57.193881, -19.8997),
                  (57.987393, -19.8997),
                  (57.987393, -20.616082)),
        projection_class=GeoProjection
    )

    print("Initializing the model...")
    start_time = datetime.datetime.now().replace(hour=6, minute=30, second=0, microsecond=0)
    model = gs.Model(
        time_step=gs.hours(6),
        start_time=start_time,
        duration=gs.days(7),
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

    print("Fetching real-time wind forecast...")
    wind_series = fetch_wind_timeseries(lat, lon, start_time)
    wind = gs.Wind(timeseries=wind_series, units='m/s', extrapolation_is_allowed=True)
    model.movers += gs.WindMover(wind)

    print("Adding oil spill...")
    try:
        oil = gs.GnomeOil(filename=OIL_FILE)
    except:
        oil = gs.nonweathering_substance()

    model.spills += gs.surface_point_line_spill(
        num_elements=10000,
        start_position=start_position,
        release_time=start_time,
        end_release_time=start_time + gs.days(4),  # 4-day release
        amount=1000,
        substance=oil,
        units='tons',
        windage_range=(0.03, 0.03),
        windage_persist=-1,
        name='Forecasted point-source spill'
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
