#!/usr/bin/env python3
"""Minimal demo: display text on WhisPlay HAT."""

import argparse
import time
from PIL import Image, ImageDraw, ImageFont
from WhisPlay import WhisPlayBoard


def create_text_image(text, width, height, bg_color=(0, 0, 0), text_color=(255, 255, 255)):
    """Create image with centered text, converted to RGB565."""
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Try to load a font
    font = None
    font_size = 32
    for fpath in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]:
        try:
            font = ImageFont.truetype(fpath, font_size)
            break
        except (IOError, OSError):
            continue

    if font is None:
        font = ImageFont.load_default()

    # Word wrap if text is too long
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] < width - 20:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    # Calculate total height and starting Y position
    line_height = font_size + 5
    total_height = len(lines) * line_height
    y = (height - total_height) // 2

    # Draw each line centered
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), line, fill=text_color, font=font)
        y += line_height

    # Convert to RGB565
    pixel_data = []
    for py in range(height):
        for px in range(width):
            r, g, b = img.getpixel((px, py))
            rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            pixel_data.append((rgb565 >> 8) & 0xFF)
            pixel_data.append(rgb565 & 0xFF)

    return pixel_data


def main():
    parser = argparse.ArgumentParser(description='Display text on WhisPlay HAT')
    parser.add_argument('--text', '-t', required=True, help='Text to display')
    parser.add_argument('--bg', default='black', help='Background color (black/white/red/green/blue)')
    parser.add_argument('--fg', default='white', help='Text color (black/white/red/green/blue)')
    args = parser.parse_args()

    colors = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
    }

    bg_color = colors.get(args.bg.lower(), (0, 0, 0))
    text_color = colors.get(args.fg.lower(), (255, 255, 255))

    board = WhisPlayBoard()
    try:
        board.set_backlight(80)
        board.set_rgb(255, 255, 255)  # White LED

        print(f"Displaying: {args.text}")
        image_data = create_text_image(
            args.text, board.LCD_WIDTH, board.LCD_HEIGHT,
            bg_color=bg_color, text_color=text_color
        )
        board.draw_image(0, 0, board.LCD_WIDTH, board.LCD_HEIGHT, image_data)

        print("Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        board.set_rgb(0, 0, 0)
        board.set_backlight(0)
        board.cleanup()


if __name__ == "__main__":
    main()
