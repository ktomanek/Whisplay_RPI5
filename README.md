# WhisPlay for Raspberry Pi 5

This is a modified fork of [PiSugar/Whisplay](https://github.com/PiSugar/Whisplay) with native Raspberry Pi 5 support.

## Why This Fork?

The original WhisPlay driver uses `RPi.GPIO`, which doesn't work on Raspberry Pi 5 due to the new RP1 GPIO controller. This fork replaces `RPi.GPIO` with `gpiozero` + `lgpio` backend for native Pi 5 compatibility.

See [README_orig.md](README_orig.md) for the original documentation (Radxa boards, full audio driver installation, etc.).

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
sudo apt install python3-lgpio python3-gpiozero python3-spidev python3-pil
```

Create a virtual environment with access to system packages:

```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
```

The `--system-site-packages` flag allows the venv to use apt-installed packages (like `python3-lgpio`) which are difficult to build via pip.

Install the WhisPlay package:

```bash
pip install -e .
```

Now you can import `WhisPlayBoard` from any Python script:

```python
from WhisPlay import WhisPlayBoard
```

## Demos

```bash
cd Driver

# Display gradient image
python demo_hat.py

# Cycle through LED colors
python demo_led.py

# Button press changes LED color
python demo_button.py

# Display an image file
python demo_image.py --file /path/to/image.png

# Display text
python demo_text.py --text "Hello World"
python demo_text.py --text "Warning!" --bg red --fg white

# Random numbers until button pressed
python demo_interrupt.py
```

### Video playback

```bash
sudo apt install ffmpeg
cd example
python play_mp4.py --file /path/to/video.mp4
```


## Audio Driver

For WM8960 audio support, see [README_orig.md](README_orig.md) for installation instructions using the original driver scripts.

## Changes from Original

- Replaced `RPi.GPIO` with `gpiozero` for Raspberry Pi 5 compatibility
- Uses `lgpio` backend (native RP1 support)
- Removed Radxa support (Pi 5 only)
- Added `setup.py` for pip installation
- Added demo scripts: `demo_hat.py`, `demo_led.py`, `demo_button.py`, `demo_image.py`, `demo_text.py`, `demo_interrupt.py`
