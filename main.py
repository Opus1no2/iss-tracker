from modules.gui import Gui
from modules.satellite import download_tle, load_satellites


def main():
    download_tle()
    satellites = load_satellites()
    gui = Gui(satellites)
    gui.header_stats()
    gui.create_canvas()
    gui.footer()
    gui.run()


if __name__ == "__main__":
    main()
