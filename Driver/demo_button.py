#!/usr/bin/env python3
"""Minimal demo: button press cycles LED color."""

import time
from WhisPlay import WhisPlayBoard

color_index = 0
colors = [
    (255, 0, 0, "Red"),
    (0, 255, 0, "Green"),
    (0, 0, 255, "Blue"),
    (255, 255, 0, "Yellow"),
    (255, 0, 255, "Magenta"),
    (0, 255, 255, "Cyan"),
    (255, 255, 255, "White"),
    (0, 0, 0, "Off"),
]


def main():
    board = WhisPlayBoard()

    def on_press():
        global color_index
        color_index = (color_index + 1) % len(colors)
        r, g, b, name = colors[color_index]
        print(f"Button pressed: {name}")
        board.set_rgb(r, g, b)

    board.on_button_press(on_press)

    try:
        board.set_backlight(50)
        board.set_rgb(255, 0, 0)
        print("Press button to change LED color. Ctrl+C to exit.")
        print("  Red")
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        board.set_rgb(0, 0, 0)
        board.set_backlight(0)
        board.cleanup()


if __name__ == "__main__":
    main()
