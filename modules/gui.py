import sv_ttk
import rasterio
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .satellite import ISS


class Gui:
    def __init__(self):
        self.root = Tk()

        self.init_root()

        self.satellite_map = SatelliteMap()
        self.iss = ISS()

    def init_root(self):
        self.root.title("ISS Tracker")
        sv_ttk.set_theme("dark")

        self.label = ttk.Label(self.root, text="ISS Location", font=("Arial", 14))
        self.label.pack(pady=10)

    def header_stats(self):
        stats_frame = ttk.Frame(self.root)
        stats_frame.pack(pady=10)

        self.speed_label = ttk.Label(
            stats_frame, text=f"Speed: {self.iss.speed():.2f} km/s"
        )
        self.speed_label.grid(row=0, column=0, padx=5)

        self.altitude_label = ttk.Label(
            stats_frame, text=f"Altitude: {self.iss.distance():.2f} km"
        )
        self.altitude_label.grid(row=0, column=1, padx=5)

    def update_header_stats(self):
        self.speed_label.config(text=f"Speed: {self.iss.speed():.2f} m/s")
        self.altitude_label.config(text=f"Altitude: {self.iss.distance():.2f} km")

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
        lat, lon = self.iss.lat_lon()

        col, row = ~self.satellite_map.src.transform * (lon.degrees, lat.degrees)
        flipped_row = self.satellite_map.src.height - row

        self.satellite_map.dot.set_data([col], [flipped_row])
        self.canvas.draw()

        self.label.config(
            text=f"ISS Location at {lat.degrees:.2f}°N, {lon.degrees:.2f}°E"
        )
        self.update_header_stats()

        self.root.after(1000, self.update_canvas)


class SatelliteMap:
    def __init__(self):
        self.image_path = "data/blue_marble.tiff"
        self.src = rasterio.open(self.image_path)
        self.fig, self.ax = plt.subplots(figsize=(15, 10))

        self.load_image()

    def load_image(self):
        image = self.src.read([1, 2, 3]).transpose((1, 2, 0))

        self.ax.set_axis_off()

        self.fig.patch.set_facecolor("#1c1c1c")

        self.ax.imshow(
            image[::-1]
        )  # Flip the image vertically to match the coordinate system

        (self.dot,) = self.ax.plot(
            [], [], marker="o", color="red", markersize=5, label="ISS Location"
        )

        self.ax.set_xlim(0, self.src.width)
        self.ax.set_ylim(0, self.src.height)
