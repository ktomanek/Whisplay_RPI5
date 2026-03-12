#!/usr/bin/env python3
"""Minimal demo: display a gradient image on WhisPlay HAT."""

import time
from WhisPlay import WhisPlayBoard


def rgb_to_rgb565(r, g, b):
    """Convert RGB888 to RGB565."""
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def create_gradient_image(width, height):
    """Create a simple blue-to-red gradient as RGB565 bytes."""
    data = []
    for y in range(height):
        for x in range(width):
            r = int(x / width * 255)
            b = int((1 - x / width) * 255)
            g = int(y / height * 128)
            color = rgb_to_rgb565(r, g, b)
            data.append((color >> 8) & 0xFF)
            data.append(color & 0xFF)
    return data


def main():
    board = WhisPlayBoard()
    try:
        board.set_backlight(80)
        image_data = create_gradient_image(board.LCD_WIDTH, board.LCD_HEIGHT)
        board.draw_image(0, 0, board.LCD_WIDTH, board.LCD_HEIGHT, image_data)
        print("Image displayed. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        board.set_backlight(0)
        board.cleanup()


if __name__ == "__main__":
    main()
