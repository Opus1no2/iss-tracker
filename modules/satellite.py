from skyfield.api import load, wgs84
from skyfield.iokit import parse_tle_file


class ISS:
    file_name = "data/iss.tle"
    data_url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle"

    def __init__(self):
        self.max_days = 3
        self.name = "ISS (ZARYA)"
        self.load_iss_data()
        self.iss = self.get_iss()

    def load_iss_data(self):
        if (
            not load.exists(ISS.file_name)
            or load.days_old(ISS.file_name) > self.max_days
        ):
            load.download(ISS.data_url, filename=ISS.file_name)

    def load_tle(self):
        ts = load.timescale()
        with load.open(ISS.file_name) as f:
            satellite = list(parse_tle_file(f, ts))
        return satellite

    def get_iss(self):
        satellites = self.load_tle()
        by_name = {sat.name: sat for sat in satellites}
        return by_name.get(self.name)

    def lat_lon(self):
        ts = load.timescale()
        t = ts.now()
        geocentric = self.iss.at(t)

        lat, lon = wgs84.latlon_of(geocentric)

        return lat, lon

    def speed(self):
        ts = load.timescale()
        t = ts.now()
        geocentric = self.iss.at(t)

        v = geocentric.velocity.km_per_s  # returns a numpy array
        v = (v[0] ** 2 + v[1] ** 2 + v[2] ** 2) ** 0.5
        v = float(v)  # Convert to float for better readability
        # convert to miles pers second
        v *= 0.621371  # 1 km/s = 0.621371 miles/s
        return v

    def distance(self):
        ts = load.timescale()
        t = ts.now()
        # geocentric = self.iss.at(t)
        lat, lon = self.lat_lon()
        bluffton = wgs84.latlon(lat.degrees, lon.degrees)
        difference = self.iss - bluffton
        topocentric = difference.at(t)
        alt, az, distance = topocentric.altaz()

        return distance.km
