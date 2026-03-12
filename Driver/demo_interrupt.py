#!/usr/bin/env python3
"""Demo: display random numbers until button is pressed to exit."""

import random
import time
from PIL import Image, ImageDraw, ImageFont
from WhisPlay import WhisPlayBoard

running = True


def create_number_image(number, width, height):
    """Create image with large centered number, converted to RGB565."""
    img = Image.new('RGB', (width, height), (0, 0, 40))
    draw = ImageDraw.Draw(img)

    # Try to load a large font
    font = None
    for fpath in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]:
        try:
            font = ImageFont.truetype(fpath, 72)
            break
        except (IOError, OSError):
            continue

    if font is None:
        font = ImageFont.load_default()

    text = str(number)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    draw.text((x, y), text, fill=(255, 255, 255), font=font)

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
    global running

    board = WhisPlayBoard()

    def on_button_press():
        global running
        print("Button pressed - exiting...")
        running = False

    board.on_button_press(on_button_press)

    try:
        board.set_backlight(80)
        board.set_rgb(0, 255, 0)  # Green LED while running

        print("Displaying random numbers. Press button to exit.")

        while running:
            number = random.randint(0, 999)
            print(f"  {number}")

            image_data = create_number_image(number, board.LCD_WIDTH, board.LCD_HEIGHT)
            board.draw_image(0, 0, board.LCD_WIDTH, board.LCD_HEIGHT, image_data)

            # Wait 0.5s but check running flag frequently
            for _ in range(10):
                if not running:
                    break
                time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nCtrl+C pressed")
    finally:
        board.set_rgb(0, 0, 0)
        board.set_backlight(0)
        board.cleanup()
        print("Cleanup done.")


if __name__ == "__main__":
    main()
