import spidev
import time

from gpiozero import DigitalOutputDevice, PWMLED, Button
from gpiozero.pins.lgpio import LGPIOFactory
from gpiozero import Device

# Use lgpio backend for Pi 5 compatibility
try:
    Device.pin_factory = LGPIOFactory()
except Exception:
    pass  # Fall back to default factory


def _detect_model():
    """Detect Raspberry Pi model"""
    try:
        with open("/proc/device-tree/model", "r") as f:
            return f.read().strip('\0').strip()
    except Exception:
        return "Unknown Raspberry Pi"


PLATFORM_MODEL = _detect_model()


# ==================== gpiozero PWM Wrapper ====================
class _GpioZeroPWMWrapper:
    """Wrapper to make gpiozero PWMLED compatible with SoftPWM interface"""

    def __init__(self, pwmled):
        self._pwmled = pwmled

    def start(self, duty_cycle=0):
        self._pwmled.value = duty_cycle / 100.0

    def ChangeDutyCycle(self, duty_cycle):
        self._pwmled.value = max(0.0, min(1.0, duty_cycle / 100.0))

    def stop(self):
        self._pwmled.off()


class WhisPlayBoard:
    # LCD parameters
    LCD_WIDTH = 240
    LCD_HEIGHT = 280
    CornerHeight = 20  # Rounded corner height in pixels

    # Physical pin definitions (BOARD mode)
    DC_PIN = 13
    RST_PIN = 7
    LED_PIN = 15

    # RGB LED pins
    RED_PIN = 22
    GREEN_PIN = 18
    BLUE_PIN = 16

    # Button pin
    BUTTON_PIN = 11

    def __init__(self):
        self.backlight_pwm = None
        self._current_r = 0
        self._current_g = 0
        self._current_b = 0
        self.button_press_callback = None
        self.button_release_callback = None

        self._init_gpio()

        self.previous_frame = None
        self._detect_hardware_version()
        self._detect_wm8960()
        self.set_backlight(0)
        self._reset_lcd()
        self._init_display()
        self.fill_screen(0)

    def _init_gpio(self):
        # Initialize LCD pins using gpiozero (BOARD pin format)
        self._dc_device = DigitalOutputDevice(f"BOARD{self.DC_PIN}")
        self._rst_device = DigitalOutputDevice(f"BOARD{self.RST_PIN}")
        self._led_device = DigitalOutputDevice(f"BOARD{self.LED_PIN}", active_high=False)
        self._led_device.on()  # Enable backlight (active low)

        # Initialize RGB LED pins using gpiozero PWMLED (active_high=False for common anode)
        self._red_pwm = PWMLED(f"BOARD{self.RED_PIN}", active_high=False, frequency=100)
        self._green_pwm = PWMLED(f"BOARD{self.GREEN_PIN}", active_high=False, frequency=100)
        self._blue_pwm = PWMLED(f"BOARD{self.BLUE_PIN}", active_high=False, frequency=100)
        # Create wrapper objects compatible with existing interface
        self.red_pwm = _GpioZeroPWMWrapper(self._red_pwm)
        self.green_pwm = _GpioZeroPWMWrapper(self._green_pwm)
        self.blue_pwm = _GpioZeroPWMWrapper(self._blue_pwm)
        self.red_pwm.start(0)
        self.green_pwm.start(0)
        self.blue_pwm.start(0)

        # Initialize button using gpiozero
        self._button = Button(f"BOARD{self.BUTTON_PIN}", pull_up=True, bounce_time=0.05)
        self._button.when_pressed = self._on_button_press
        self._button.when_released = self._on_button_release

        # Initialize SPI
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 100_000_000
        self.spi.mode = 0b00

    def _on_button_press(self):
        if self.button_press_callback:
            self.button_press_callback()

    def _on_button_release(self):
        if self.button_release_callback:
            self.button_release_callback()

    def _gpio_output(self, pin, value):
        """Set GPIO pin output value"""
        if pin == self.DC_PIN:
            self._dc_device.value = 1 if value else 0
        elif pin == self.RST_PIN:
            self._rst_device.value = 1 if value else 0
        elif pin == self.LED_PIN:
            self._led_device.value = 1 if value else 0

    # ==================== Hardware Detection ====================
    def _detect_hardware_version(self):
        """Detect hardware version and set backlight mode accordingly"""
        try:
            model = PLATFORM_MODEL
            if "Zero" in model and "2" not in model:
                self.backlight_mode = False  # Use simple on/off mode
            else:
                self.backlight_mode = True  # Use PWM mode
            print(f"Detected hardware: {model}, Backlight mode: {'PWM' if self.backlight_mode else 'Simple Switch'}")
        except Exception as e:
            print(f"Error detecting hardware version: {e}")
            self.backlight_mode = True

    def _detect_wm8960(self):
        """Detect if a sound card containing wm8960 exists"""
        try:
            with open("/proc/asound/cards", "r") as f:
                for line in f:
                    if "wm8960" in line.lower():
                        print("wm8960 sound card detected.")
                        return True
        except Exception as e:
            print(f"Error detecting wm8960 sound card: {e}")
            return False

        print("wm8960 sound card not detected. Please refer to the following page for installation instructions.")
        print("https://docs.pisugar.com/")
        return False

    # ========== Backlight Control ==========
    def set_backlight(self, brightness):
        if self.backlight_mode:  # PWM mode
            if self.backlight_pwm is None:
                # Close the original DigitalOutputDevice first to release the pin
                self._led_device.close()
                # Create a PWMLED wrapper for backlight
                self._backlight_pwmled = PWMLED(f"BOARD{self.LED_PIN}", active_high=False, frequency=1000)
                self.backlight_pwm = _GpioZeroPWMWrapper(self._backlight_pwmled)
                self.backlight_pwm.start(100)
            if 0 <= brightness <= 100:
                duty_cycle = 100 - brightness
                self.backlight_pwm.ChangeDutyCycle(duty_cycle)
        else:  # Simple on/off mode
            if brightness == 0:
                self._gpio_output(self.LED_PIN, 1)  # Turn off backlight
            else:
                self._gpio_output(self.LED_PIN, 0)  # Turn on backlight

    def set_backlight_mode(self, mode):
        """
        Set backlight mode
        :param mode: True for PWM brightness control, False for simple on/off
        """
        if mode == self.backlight_mode:
            return  # Mode unchanged, no action needed

        if mode:  # Switch to PWM mode
            # Close the original DigitalOutputDevice first to release the pin
            if hasattr(self, '_led_device') and self._led_device:
                self._led_device.close()
            self._backlight_pwmled = PWMLED(f"BOARD{self.LED_PIN}", active_high=False, frequency=1000)
            self.backlight_pwm = _GpioZeroPWMWrapper(self._backlight_pwmled)
            self.backlight_pwm.start(100)
        else:  # Switch to simple on/off mode
            if self.backlight_pwm is not None:
                self.backlight_pwm.stop()
                self.backlight_pwm = None
            self._gpio_output(self.LED_PIN, 1)  # Ensure backlight is on
        self.backlight_mode = mode

    def _reset_lcd(self):
        self._gpio_output(self.RST_PIN, 1)
        time.sleep(0.1)
        self._gpio_output(self.RST_PIN, 0)
        time.sleep(0.1)
        self._gpio_output(self.RST_PIN, 1)
        time.sleep(0.12)

    def _init_display(self):
        self._send_command(0x11)
        time.sleep(0.12)
        USE_HORIZONTAL = 1
        direction = {0: 0x00, 1: 0xC0, 2: 0x70, 3: 0xA0}.get(USE_HORIZONTAL, 0x00)
        self._send_command(0x36, direction)
        self._send_command(0x3A, 0x05)
        self._send_command(0xB2, 0x0C, 0x0C, 0x00, 0x33, 0x33)
        self._send_command(0xB7, 0x35)
        self._send_command(0xBB, 0x32)
        self._send_command(0xC2, 0x01)
        self._send_command(0xC3, 0x15)
        self._send_command(0xC4, 0x20)
        self._send_command(0xC6, 0x0F)
        self._send_command(0xD0, 0xA4, 0xA1)
        self._send_command(0xE0, 0xD0, 0x08, 0x0E, 0x09, 0x09, 0x05, 0x31, 0x33, 0x48, 0x17, 0x14, 0x15, 0x31, 0x34)
        self._send_command(0xE1, 0xD0, 0x08, 0x0E, 0x09, 0x09, 0x15, 0x31, 0x33, 0x48, 0x17, 0x14, 0x15, 0x31, 0x34)
        self._send_command(0x21)
        self._send_command(0x29)

    def _send_command(self, cmd, *args):
        self._gpio_output(self.DC_PIN, 0)
        self.spi.xfer2([cmd])
        if args:
            self._gpio_output(self.DC_PIN, 1)
            self._send_data(list(args))

    def _send_data(self, data):
        self._gpio_output(self.DC_PIN, 1)
        try:
            self.spi.writebytes2(data)
        except AttributeError:
            max_chunk = 4096
            for i in range(0, len(data), max_chunk):
                self.spi.writebytes(data[i : i + max_chunk])

    def set_window(self, x0, y0, x1, y1, use_horizontal=0):
        if use_horizontal in (0, 1):
            self._send_command(0x2A, x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF)
            self._send_command(0x2B, (y0 + 20) >> 8, (y0 + 20) & 0xFF, (y1 + 20) >> 8, (y1 + 20) & 0xFF)
        elif use_horizontal in (2, 3):
            self._send_command(0x2A, (x0 + 20) >> 8, (x0 + 20) & 0xFF, (x1 + 20) >> 8, (x1 + 20) & 0xFF)
            self._send_command(0x2B, y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF)
        self._send_command(0x2C)

    def draw_pixel(self, x, y, color):
        if x >= self.LCD_WIDTH or y >= self.LCD_HEIGHT:
            return
        self.set_window(x, y, x, y)
        self._send_data([(color >> 8) & 0xFF, color & 0xFF])

    def draw_line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            self.draw_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def fill_screen(self, color):
        self.set_window(0, 0, self.LCD_WIDTH - 1, self.LCD_HEIGHT - 1)
        buffer = []
        high = (color >> 8) & 0xFF
        low = color & 0xFF
        for _ in range(self.LCD_WIDTH * self.LCD_HEIGHT):
            buffer.extend([high, low])
        self._send_data(buffer)

    def draw_image(self, x, y, width, height, pixel_data):
        if (x + width > self.LCD_WIDTH) or (y + height > self.LCD_HEIGHT):
            raise ValueError("Image dimensions exceed screen bounds")
        self.set_window(x, y, x + width - 1, y + height - 1)
        self._send_data(pixel_data)

    # ========== RGB LED & Button ==========
    def set_rgb(self, r, g, b):
        self.red_pwm.ChangeDutyCycle(100 - (r / 255 * 100))
        self.green_pwm.ChangeDutyCycle(100 - (g / 255 * 100))
        self.blue_pwm.ChangeDutyCycle(100 - (b / 255 * 100))
        self._current_r = r
        self._current_g = g
        self._current_b = b

    def set_rgb_fade(self, r_target, g_target, b_target, duration_ms=100):
        steps = 20
        delay_ms = duration_ms / steps

        r_step = (r_target - self._current_r) / steps
        g_step = (g_target - self._current_g) / steps
        b_step = (b_target - self._current_b) / steps

        for i in range(steps + 1):
            r_interim = int(self._current_r + i * r_step)
            g_interim = int(self._current_g + i * g_step)
            b_interim = int(self._current_b + i * b_step)
            self.set_rgb(
                max(0, min(255, r_interim)),
                max(0, min(255, g_interim)),
                max(0, min(255, b_interim)),
            )
            time.sleep(delay_ms / 1000.0)

    def button_pressed(self):
        return self._button.is_pressed

    def on_button_press(self, callback):
        self.button_press_callback = callback

    def on_button_release(self, callback):
        self.button_release_callback = callback

    # ========== Cleanup ==========
    def cleanup(self):
        # Stop backlight PWM
        if self.backlight_pwm is not None:
            self.backlight_pwm.stop()
        # Close SPI
        self.spi.close()
        # Stop RGB LED PWM
        self.red_pwm.stop()
        self.green_pwm.stop()
        self.blue_pwm.stop()

        # Close gpiozero devices
        self._dc_device.close()
        self._rst_device.close()
        if hasattr(self, '_backlight_pwmled'):
            self._backlight_pwmled.close()
        else:
            self._led_device.close()
        self._red_pwm.close()
        self._green_pwm.close()
        self._blue_pwm.close()
        self._button.close()
