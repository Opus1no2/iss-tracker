from modules.gui import Gui


def main():
    gui = Gui()
    gui.header_stats()
    gui.create_canvas()
    gui.footer()
    gui.run()


if __name__ == "__main__":
    main()
