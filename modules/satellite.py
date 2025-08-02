from skyfield.api import load, wgs84
from skyfield.iokit import parse_tle_file
from functools import cache

file_name = "data/iss.tle"


def download_tle():
    max_days = 3
    data_url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle"

    if not load.exists(file_name) or load.days_old(file_name) > max_days:
        load.download(data_url, filename=file_name)


@cache
def load_satellites():
    ts = load.timescale()
    with load.open(file_name) as f:
        satellites = list(parse_tle_file(f, ts))

    return satellites


def find_by_name(name, satellites):
    by_name = {sat.name: sat for sat in satellites}
    return by_name.get(name)


def lat_lon_of(satellite):
    ts = load.timescale()
    t = ts.now()

    geocentric = satellite.at(t)

    lat, lon = wgs84.latlon_of(geocentric)

    return lat, lon


def lat_longs():
    _lat_longs = []
    satellites = load_satellites()

    for _, satellite in satellites.items():
        lat, lon = lat_lon_of(satellite)
        _lat_longs.append((lat.degrees, lon.degrees))

    return _lat_longs


def speed_of(satellite):
    ts = load.timescale()
    t = ts.now()
    geocentric = satellite.at(t)

    v = geocentric.velocity.km_per_s  # returns a numpy array
    v = (v[0] ** 2 + v[1] ** 2 + v[2] ** 2) ** 0.5
    v = float(v)  # Convert to float for better readability
    # convert to miles per second
    v *= 0.621371  # 1 km/s = 0.621371 miles/s
    return v


def distance_of(satellite):
    ts = load.timescale()
    t = ts.now()
    lat, lon = lat_lon_of(satellite)
    bluffton = wgs84.latlon(lat.degrees, lon.degrees)
    difference = satellite - bluffton
    topocentric = difference.at(t)
    alt, az, distance = topocentric.altaz()

    return distance.km
