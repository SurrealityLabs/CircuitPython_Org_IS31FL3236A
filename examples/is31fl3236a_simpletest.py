# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 Randy Glenn
# SPDX-License-Identifier: MIT

# This simple test outputs a 50% duty cycle PWM signal on channel 0. Connect an LED
# cathode to the pin, and the LED's anode to the supply voltage, to see duty cycle /
# brightness changes.

from board import SCL, SDA
import busio

# Import the IS31FL3236A module
from is31fl3236a import IS31FL3236A

# Create the I2C bus interface
i2c_bus = busio.I2C(SCL, SDA)

# Create a simple IS31FL3236A class instance
is31fl = IS31FL3236A(i2c_bus)

# PWM frequency is 3 KHz by default, which should be fine

# Set the PWM duty cycle for channel 0 to 50%. duty_cycle is 16 bits to match other PWM objects,
# but the IS31FL3236A will only actually give 8 bits of resolution.
is31fl.channels[0].duty_cycle = 0x7FFF
