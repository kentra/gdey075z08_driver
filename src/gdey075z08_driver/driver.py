##
#  @filename   :   epd7in5.py
#  @brief      :   Implements for Dual-color e-paper library
#  @author     :   Yehui from Waveshare
#
#  Copyright (C) Waveshare     July 10 2017
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import logging
import time
import spidev
from typing import Tuple

import RPi.GPIO as GPIO

# from . import epdif
from gdey075z08_driver.static import Static


class EPD:
    def __init__(
        self,
        reset_pin: int,
        cs_pin: int,
        dc_pin: int,
        busy_pin: int,
        red_bounds: Tuple[int, int] = (64, 192),
    ) -> None:
        """Constructs an EPD controller
        :param red_bounds: the (max, min) threshold for red pixels.
        Specifically, if a pixel's grayscale value is no smaller and no
        larger than the bounds, it will be considered red.
        """  # noqa: D205
        self.reset_pin: int = reset_pin
        self.busy_pin: int = busy_pin
        self.cs_pin: int = cs_pin
        self.dc_pin: int = dc_pin
        self.width: int = Static.EPD_WIDTH
        self.height: int = Static.EPD_HEIGHT
        self.red_bounds: tuple[int, int] = red_bounds
        self.__spi_init()

    def __spi_init(self) -> int:
        self.SPI = spidev.SpiDev(0, 0)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.reset_pin, GPIO.OUT)
        GPIO.setup(self.dc_pin, GPIO.OUT)
        GPIO.setup(self.cs_pin, GPIO.OUT)
        GPIO.setup(self.busy_pin, GPIO.IN)
        self.SPI.max_speed_hz = 2000000
        self.SPI.mode = 0b00
        return 0

    def __spi_transfer(self, data) -> None:
        self.SPI.writebytes(data)

    def digital_write(self, pin, value) -> None:
        # SPI device, bus = 0, device = 0
        GPIO.output(pin, value)

    def digital_read(self, pin) -> bool:
        return GPIO.input(pin)

    def delay_ms(self, delaytime) -> None:
        time.sleep(delaytime / 1000.0)

    def send_command(self, command) -> None:
        self.digital_write(self.dc_pin, GPIO.LOW)
        # the parameter type is list but not int
        # so use [command] instead of command
        self.__spi_transfer([command])

    def send_data(self, data) -> None:
        self.digital_write(self.dc_pin, GPIO.HIGH)
        # the parameter type is list but not int
        # so use [data] instead of data
        self.__spi_transfer([data])

    def init(self) -> int:
        if self.__spi_init() != 0:
            return -1
        logging.info("Initialization begin")
        self.reset()
        self.send_command(Static.POWER_SETTING)
        self.send_data(0x07)
        self.send_data(0x07)
        self.send_data(0x3F)
        self.send_data(0x3F)

        logging.info("Power on")
        self.send_command(Static.POWER_ON)
        self.wait_until_idle()

        self.send_command(Static.PANEL_SETTING)
        self.send_data(0x0F)

        self.send_command(0x15)
        self.send_data(0x00)

        logging.info("VCOM and data intervals set")
        self.send_command(Static.VCOM_AND_DATA_INTERVAL_SETTING)
        self.send_data(0x11)
        self.send_data(0x07)

        logging.info("Tcon set")
        self.send_command(Static.TCON_SETTING)
        self.send_data(Static.LUT_WHITE)
        return 0

    def wait_until_idle(self):
        busy = True
        while busy:
            self.send_command(Static.GET_STATUS)
            busy = self.digital_read(self.busy_pin) == 0x00

    def reset(self):
        self.digital_write(self.reset_pin, GPIO.LOW)  # module reset
        self.delay_ms(200)
        self.digital_write(self.reset_pin, GPIO.HIGH)
        self.delay_ms(200)

    def get_frame_buffer(self, image):
        buf_w = [0xFF] * int(self.height * self.width / 8)
        buf_r = [0x00] * int(self.height * self.width / 8)
        # Set buffer to value of Python Imaging Library image.
        # Image must be in mode L.
        image_grayscale = image.convert("L")
        imwidth, imheight = image_grayscale.size
        if imwidth != self.width or imheight != self.height:
            raise ValueError(
                "Image must be same dimensions as display \
                ({0}x{1}).".format(self.width, self.height)
            )

        pixels = image_grayscale.load()
        for y in range(self.height):
            for x in range(int(self.width / 8)):
                sign_w = 0xFF
                sign_r = 0x00
                for i in range(0, 8):
                    p = pixels[x * 8 + i, y]
                    if p < self.red_bounds[0]:
                        sign_w &= ~(0x80 >> i)
                    elif p < self.red_bounds[1]:
                        sign_r |= 0x80 >> i
                index = x + int(y * self.width / 8)
                buf_w[index] = sign_w
                buf_r[index] = sign_r
        return buf_w, buf_r

    def display_frame(self, frame_buffer):
        buf_w, buf_r = frame_buffer

        def write_buffer(buf):
            for data in buf:
                self.send_data(data)

        self.send_command(Static.DATA_START_TRANSMISSION_1)
        write_buffer(buf_w)
        self.send_command(Static.DATA_START_TRANSMISSION_2)
        write_buffer(buf_r)

        self.send_command(Static.DISPLAY_REFRESH)
        self.delay_ms(100)
        self.wait_until_idle()

    def sleep(self):
        self.send_command(Static.POWER_OFF)
        self.wait_until_idle()
        self.send_command(Static.DEEP_SLEEP)
        self.send_data(0xA5)
