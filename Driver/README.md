# WhisPlay for Raspberry Pi 5

Modified from the original repo to use gpiozero instead of RPi.GPIO for native Pi 5 support.

Python module for the WhisPlay HAT display board.

## Hardware Setup

Enable SPI:

```bash
sudo raspi-config
# Interface Options -> SPI -> Enable
```

Or add to `/boot/firmware/config.txt`:

```
dtparam=spi=on
```

Then reboot.

## Installation

Install system packages:

```bash
sudo apt install python3-lgpio python3-gpiozero python3-spidev
```

Create a virtual environment with access to system packages:

```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
```

The `--system-site-packages` flag allows the venv to use apt-installed packages (like `python3-lgpio`) which are difficult to build via pip.

## Demos

From the Driver folder:

```bash
cd Driver
source venv/bin/activate

# Display gradient image
python demo_hat.py

# Cycle through LED colors
python demo_led.py

# Button press changes LED color
python demo_button.py
```

## Usage

```python
from WhisPlay import WhisPlayBoard

board = WhisPlayBoard()
board.set_backlight(80)
board.fill_screen(0x001F)  # Blue
board.set_rgb(255, 0, 0)   # Red LED
board.cleanup()
```

From the `example/` folder:

```python
import sys, os
sys.path.append(os.path.abspath("../Driver"))
from WhisPlay import WhisPlayBoard
```
