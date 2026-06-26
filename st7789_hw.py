import time
import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

# =========================
# HARDWARE CLASS
# -> specific for Aliexpress Display
# -> if you use anything else, modify or use
#    the provided class instead!
# =========================

class ST7789_HW:
    def __init__(
        self,
        width,
        height,
        dc,
        rst,
        spi_port=0,
        spi_device=0,
        speed=32000000,
        x_offset=0,
        y_offset=0,
        rotation=0
    ):
        self.base_width = width
        self.base_height = height

        self.dc = dc
        self.rst = rst

        self.x_offset = x_offset
        self.y_offset = y_offset
        self.rotation = rotation % 360

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(dc, GPIO.OUT)
        GPIO.setup(rst, GPIO.OUT)

        self.spi = spidev.SpiDev()
        self.spi.open(spi_port, spi_device)
        self.spi.max_speed_hz = speed
        self.spi.mode = 0

        self.reset()

    def reset(self):
        GPIO.output(self.rst, 1)
        time.sleep(0.05)
        GPIO.output(self.rst, 0)
        time.sleep(0.1)
        GPIO.output(self.rst, 1)
        time.sleep(0.15)

    def cmd(self, c):
        GPIO.output(self.dc, 0)
        self.spi.xfer([c])

    def data(self, d):
        GPIO.output(self.dc, 1)
        if isinstance(d, list):
            self.spi.xfer(d)
        else:
            self.spi.xfer([d])

    def init(self):
        self.cmd(0x01)
        time.sleep(0.15)

        self.cmd(0x11)
        time.sleep(0.2)

        self.cmd(0x3A)
        self.data(0x55)

        self.cmd(0x36)
        self.data(0x00)

        self.cmd(0x29)

    # -----------------------------
    # Rotation helper
    # -----------------------------
    def _apply_rotation(self, img):
        if self.rotation == 90:
            return img.transpose(Image.ROTATE_270)
        if self.rotation == 180:
            return img.transpose(Image.ROTATE_180)
        if self.rotation == 270:
            return img.transpose(Image.ROTATE_90)
        return img

    # -----------------------------
    # Window
    # -----------------------------
    def set_window(self, x0, y0, x1, y1):
        x0 += self.x_offset
        x1 += self.x_offset
        y0 += self.y_offset
        y1 += self.y_offset

        self.cmd(0x2A)
        self.data([
            (x0 >> 8) & 0xFF,
            x0 & 0xFF,
            (x1 >> 8) & 0xFF,
            x1 & 0xFF
        ])

        self.cmd(0x2B)
        self.data([
            (y0 >> 8) & 0xFF,
            y0 & 0xFF,
            (y1 >> 8) & 0xFF,
            y1 & 0xFF
        ])

        self.cmd(0x2C)

    # -----------------------------
    # Push image
    # -----------------------------
    def image(self, img):
        img = img.convert("RGB")
        img = self._apply_rotation(img)

        pixels = img.load()
        width, height = img.size

        self.set_window(0, 0, width - 1, height - 1)

        GPIO.output(self.dc, 1)

        buf = []

        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]

                color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

                buf.append((color >> 8) & 0xFF)
                buf.append(color & 0xFF)

                if len(buf) >= 4096:
                    self.spi.xfer(buf)
                    buf = []

        if buf:
            self.spi.xfer(buf)

    # -----------------------------
    # Convenience: clear screen
    # -----------------------------
    def fill(self, color):
        img = Image.new("RGB", (self.base_width, self.base_height), color)
        self.image(img)

    # -----------------------------
    # Convenience: draw text image
    # -----------------------------
    def text(self, text, x=0, y=0, color=(255, 255, 255), font=None):
        img = Image.new("RGB", (self.base_width, self.base_height), (0, 0, 0))
        draw = ImageDraw.Draw(img)

        if font:
            draw.text((x, y), text, fill=color, font=font)
        else:
            draw.text((x, y), text, fill=color)

        self.image(img)
