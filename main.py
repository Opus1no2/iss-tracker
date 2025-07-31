from skyfield.api import load, wgs84
from skyfield.iokit import parse_tle_file

import rasterio
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

file_name = "data/iss.tle"


def fetch_iss(file_name):
    max_days = 3

    url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle"

    if not load.exists(file_name) or load.days_old(file_name) > max_days:
        load.download(url, filename=file_name)


def load_iss(file_name):
    ts = load.timescale()

    with load.open(file_name) as f:
        satellite = list(parse_tle_file(f, ts))

    return satellite


def update(frame, iss, src, ax, dot):
    ts = load.timescale()

    t = ts.now()
    geocentric = iss.at(t)

    lat, lon = wgs84.latlon_of(geocentric)

    col, row = ~src.transform * (lon.degrees, lat.degrees)
    flipped_row = src.height - row

    dot.set_data([col], [flipped_row])
    ax.set_title(f"ISS Location at {lat.degrees:.2f}°N, {lon.degrees:.2f}°E")

    return (dot,)


def main():
    fetch_iss(file_name)
    satellites = load_iss(file_name)

    by_name = {sat.name: sat for sat in satellites}
    iss = by_name.get("ISS (ZARYA)", None)

    if iss is None:
        raise ValueError("ISS not found in the TLE file.")

    path = "data/blue_marble.tiff"

    src = rasterio.open(path)

    image = src.read([1, 2, 3]).transpose((1, 2, 0))

    fig, ax = plt.subplots(figsize=(10, 10))

    ax.imshow(image[::-1])  # Flip the image vertically to match the coordinate system
    (dot,) = ax.plot(
        [], [], marker="o", color="red", markersize=5, label="ISS Location"
    )

    # Optional: force limits to image bounds
    ax.set_xlim(0, src.width)
    ax.set_ylim(0, src.height)

    geocentric = iss.at(load.timescale().now())
    iss_lat, iss_lon = wgs84.latlon_of(geocentric)

    ax.set_title(f"ISS Location at {iss_lat.degrees:.2f}°N, {iss_lon.degrees:.2f}°E")

    ax.legend()

    ani = FuncAnimation(fig, update, fargs=(iss, src, ax, dot), interval=1000)
    plt.show()


if __name__ == "__main__":
    main()
