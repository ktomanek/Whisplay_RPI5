#!/usr/bin/env python3
"""Minimal demo: cycle through RGB LED colors."""

import time
from WhisPlay import WhisPlayBoard


def main():
    board = WhisPlayBoard()
    try:
        board.set_backlight(50)

        colors = [
            (255, 0, 0, "Red"),
            (0, 255, 0, "Green"),
            (0, 0, 255, "Blue"),
            (255, 255, 0, "Yellow"),
            (255, 0, 255, "Magenta"),
            (0, 255, 255, "Cyan"),
            (255, 255, 255, "White"),
        ]

        print("Cycling LED colors. Press Ctrl+C to exit.")
        while True:
            for r, g, b, name in colors:
                print(f"  {name}")
                board.set_rgb(r, g, b)
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        board.set_rgb(0, 0, 0)
        board.set_backlight(0)
        board.cleanup()


if __name__ == "__main__":
    main()
