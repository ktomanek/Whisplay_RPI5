#!/usr/bin/env python3
"""Minimal demo: display a PNG/JPG image on WhisPlay HAT."""

import argparse
import time
from PIL import Image
from WhisPlay import WhisPlayBoard


def load_image_rgb565(filepath, width, height):
    """Load and convert image to RGB565 format."""
    img = Image.open(filepath).convert('RGB')

    # Scale to fit display while maintaining aspect ratio
    img_ratio = img.width / img.height
    disp_ratio = width / height

    if img_ratio > disp_ratio:
        new_width = width
        new_height = int(width / img_ratio)
    else:
        new_height = height
        new_width = int(height * img_ratio)

    img = img.resize((new_width, new_height), Image.LANCZOS)

    # Center on display
    x_offset = (width - new_width) // 2
    y_offset = (height - new_height) // 2

    # Create black background
    background = Image.new('RGB', (width, height), (0, 0, 0))
    background.paste(img, (x_offset, y_offset))

    # Convert to RGB565
    pixel_data = []
    for y in range(height):
        for x in range(width):
            r, g, b = background.getpixel((x, y))
            rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            pixel_data.append((rgb565 >> 8) & 0xFF)
            pixel_data.append(rgb565 & 0xFF)

    return pixel_data


def main():
    parser = argparse.ArgumentParser(description='Display image on WhisPlay HAT')
    parser.add_argument('--file', '-f', required=True, help='Path to image file (PNG/JPG)')
    args = parser.parse_args()

    board = WhisPlayBoard()
    try:
        board.set_backlight(80)
        board.set_rgb(0, 0, 255)  # Blue LED

        print(f"Loading: {args.file}")
        image_data = load_image_rgb565(args.file, board.LCD_WIDTH, board.LCD_HEIGHT)

        print(f"Displaying on {board.LCD_WIDTH}x{board.LCD_HEIGHT}")
        board.draw_image(0, 0, board.LCD_WIDTH, board.LCD_HEIGHT, image_data)

        print("Image displayed. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    except FileNotFoundError:
        print(f"Error: File not found: {args.file}")
    finally:
        board.set_rgb(0, 0, 0)
        board.set_backlight(0)
        board.cleanup()


if __name__ == "__main__":
    main()
