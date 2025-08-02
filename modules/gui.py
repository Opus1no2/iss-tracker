import sv_ttk
import rasterio
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .satellite import find_by_name, speed_of, distance_of, lat_lon_of
from matplotlib import cm


class Gui:
    def __init__(self, satellites=[]):
        self.root = Tk()

        self.init_root()
        self.satellites = satellites
        self.satellite_map = SatelliteMap(satellites)

    def init_root(self):
        self.root.title("Space Station Tracker")
        sv_ttk.set_theme("dark")

        self.label = ttk.Label(self.root, text="Space Stations", font=("Arial", 16))
        self.label.pack(pady=10)

    def header_stats(self):
        stats_frame = ttk.Frame(self.root)
        stats_frame.pack(pady=10)

        self.selected_label = ttk.Label(
            stats_frame,
            text="Satellite: " + self.satellite_map.selected_satellite.name,
            font=("Arial", 14),
        )
        self.selected_label.grid(row=1, column=0, columnspan=2, pady=5)

        self.speed_label = ttk.Label(
            stats_frame,
            text=f"Speed: {speed_of(self.satellite_map.selected_satellite):.2f} km/s",
            font=("Arial", 14),
        )

        self.speed_label.grid(row=0, column=0, padx=5)

        self.altitude_label = ttk.Label(
            stats_frame,
            text=f"Altitude: {distance_of(self.satellite_map.selected_satellite):.2f} km",
            font=("Arial", 14),
        )
        self.altitude_label.grid(row=0, column=1, padx=5)

    def update_header_stats(self):
        self.selected_label.config(
            text="Satellite: " + self.satellite_map.selected_satellite.name
        )

        self.speed_label.config(
            text=f"Speed: {speed_of(self.satellite_map.selected_satellite):.2f} m/s"
        )
        self.altitude_label.config(
            text=f"Altitude: {distance_of(self.satellite_map.selected_satellite):.2f} km"
        )

    def create_canvas(self):
        self.canvas = FigureCanvasTkAgg(self.satellite_map.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def footer(self):
        quit_button = ttk.Button(self.root, text="Quit", command=self.root.quit)
        quit_button.pack(pady=10)

    def run(self):
        self.update_canvas()
        self.root.mainloop()

    def update_canvas(self):
        for sat in self.satellites:
            lat, lon = lat_lon_of(sat)

            col, row = ~self.satellite_map.src.transform * (lon.degrees, lat.degrees)
            flipped_row = self.satellite_map.src.height - row

            self.satellite_map.sat_dots[sat.name].set_data([col], [flipped_row])

        self.canvas.draw()

        # self.label.config(
        #    text=f"ISS Location at {lat.degrees:.2f}°N, {lon.degrees:.2f}°E"
        # )
        self.update_header_stats()
        self.root.after(1000, self.update_canvas)


class SatelliteMap:
    def __init__(self, satellites):
        self.sat_dots = {}
        self.image_path = "data/blue_marble.tiff"
        self.src = rasterio.open(self.image_path)
        self.fig, self.ax = plt.subplots(figsize=(15, 10))
        self.satellites = satellites
        self.load_image()
        self.selected_satellite = find_by_name("ISS (ZARYA)", self.satellites)
        self.cid = self.fig.canvas.mpl_connect("button_press_event", self.on_click)

    def on_click(self, event):
        if event.inaxes != self.ax:
            return

        x, y = event.xdata, event.ydata
        for sat_name, dot in self.sat_dots.items():
            if dot.contains(event)[0]:
                print(f"Clicked on {sat_name} at ({x}, {y})")
                self.selected_satellite = find_by_name(sat_name, self.satellites)
                break

    def load_image(self):
        image = self.src.read([1, 2, 3]).transpose((1, 2, 0))

        self.ax.set_axis_off()

        self.fig.patch.set_facecolor("#1c1c1c")

        # Flip the image vertically to match the coordinate system
        self.ax.imshow(image[::-1])
        num_stats = len(self.satellites)
        colors = cm.get_cmap("tab10", num_stats)

        for i, sat in enumerate(self.satellites):
            (self.sat_dots[sat.name],) = self.ax.plot(
                [0], [0], marker="o", color=colors(i), markersize=5, label=sat.name
            )

        self.ax.set_xlim(0, self.src.width)
        self.ax.set_ylim(0, self.src.height)
