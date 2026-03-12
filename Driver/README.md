# WhisPlay

Python module for the WhisPlay HAT display board. Supports Raspberry Pi 5 and Radxa boards.

## Hardware Setup

### Raspberry Pi 5

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

### Raspberry Pi 5

```bash
sudo apt install python3-spidev
pip install gpiozero lgpio spidev
```

### Radxa Boards

```bash
sudo apt install python3-libgpiod python3-spidev
```

## Usage

From the `example/` folder or any script that adds the Driver path:

```python
import sys, os
sys.path.append(os.path.abspath("../Driver"))
from WhisPlay import WhisPlayBoard

board = WhisPlayBoard()
board.set_backlight(80)
board.fill_screen(0x001F)  # Blue
board.cleanup()
```

## Demo

From the Driver folder:

```bash
python demo_hat.py
```

Displays a gradient image. Press Ctrl+C to exit.
