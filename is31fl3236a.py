# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 Randy Glenn
#
# SPDX-License-Identifier: MIT
"""
`is31fl3236a`
================================================================================

CircuitPython helper library for the IS31FL3236A LED driver IC


* Author(s): Randy Glenn

Implementation Notes
--------------------

**Hardware:**

.. todo:: Add links to any specific hardware product page(s), or category page(s).
  Use unordered list & hyperlink rST inline format: "* `Link Text <url>`_"

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases
* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
* Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

# imports

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/SurrealityLabs/CircuitPython_Org_IS31FL3236A.git"

import time

from adafruit_register.i2c_struct import UnaryStruct
from adafruit_register.i2c_struct_array import StructArray
from adafruit_bus_device import i2c_device


class PWMChannel:
    """A single IS31FL3236A channel that matches the :py:class:`~pwmio.PWMOut` API."""

    def __init__(self, is31fl, index):
        self._is31fl = is31fl
        self._index = index

    @property
    def frequency(self):
        """The overall PWM frequency in Hertz (read-only).
        A PWMChannel's frequency cannot be set individually.
        All channels share a common frequency, set by IS31FL3236A.frequency."""
        return self._is31fl.frequency

    @frequency.setter
    def frequency(self, _):
        raise NotImplementedError("frequency cannot be set on individual channels")

    @property
    def duty_cycle(self):
        """16 bit value that dictates how much of one cycle is high (1) versus low (0). 0xffff will
        always be high, 0 will always be low and 0x7fff will be half high and then half low."""
        pwm = self._is31fl.pwm_regs[self._index]
        return pwm << 8

    @duty_cycle.setter
    def duty_cycle(self, value):
        if not 0 <= value <= 0xFFFF:
            raise ValueError("Out of range")

        if value == 0x0000:
            self._is31fl.led_regs[self._index] = 0x00
        else:
            # Shift our value by four because the IS31FL3236A is only 8 bits but our value is 16
            value = value >> 8
            self._is31fl.pwm_regs[self._index] = value
			self._is31fl.led_regs[self._index] = 0x01
			
		self._is31fl.apply_reg = 0x00


class IS31FLChannels:  # pylint: disable=too-few-public-methods
    """Lazily creates and caches channel objects as needed. Treat it like a sequence."""

    def __init__(self, is31fl):
        self._is31fl = is31fl
        self._channels = [None] * len(self)

    def __len__(self):
        return 36

    def __getitem__(self, index):
        if not self._channels[index]:
            self._channels[index] = PWMChannel(self._is31fl, index)
        return self._channels[index]


class IS31FL3236A:
    """
    Initialise the IS31FL3236A chip at ``address`` on ``i2c_bus``.

    :param ~busio.I2C i2c_bus: The I2C bus which the IS31FL3236A is connected to.
    :param int address: The I2C address of the IS31FL3236A.
    :param int reference_clock_speed: The frequency of the internal reference clock in Hertz.
    """

    # Registers:
	shutdown_reg = UnaryStruct(0x00, "<B")
	pwm_regs = UnaryStructArray(0x01, "<B", 36)
	apply_reg = UnaryStruct(0x25, "<B")
	led_regs = UnaryStructArray(0x26, "<B", 36)
	global_control_reg = UnaryStruct(0x4A, "<B")
	frequency_reg = UnaryStruct(0x4B, "<B")
	reset_reg = UnaryStruct(0x4C, "<B")

    def __init__(self, i2c_bus, *, address=0x3C):
        self.i2c_device = i2c_device.I2CDevice(i2c_bus, address)
        self.channels = IS31FLChannels(self)
        """Sequence of 36 `PWMChannel` objects. One for each channel."""
        self.reset()

    def reset(self):
        """Reset the chip."""
        self.reset_reg = 0x00
		self.shutdown_reg = 0x01

    @property
    def frequency(self):
        """The overall PWM frequency in Hertz. Valid values for IS31FL3236A are 3000 Hz and 22000 Hz"""
        if self.frequency_reg == 0x00:
			return 3000
		else:
			return 220000

    @frequency.setter
    def frequency(self, freq):
		if freq == 3000:
			self.frequency_reg = 0x00
		elif freq == 22000:
			self.frequency_reg = 0x01
		else:
			raise ValueError("IS31FL3236A cannot output at the given frequency")

	def __enter__(self):
		return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.deinit()

    def deinit(self):
        """Stop using the IS31FL3236A."""
        self.reset()
