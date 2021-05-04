# -*- coding: utf-8 -*-
"""
@file mma845x.py
This file contains a MicroPython driver for the MMA8451 and MMA8452
accelerometers. 

@author JR Ridgely
@copyright GPL Version 3.0
"""

import micropython


## The register address of the STATUS register in the MMA845x
STATUS_REG = micropython.const (0x00)

## The register address of the OUT_X_MSB register in the MMA845x
OUT_X_MSB = micropython.const (0x01)

## The register address of the OUT_X_LSB register in the MMA845x
OUT_X_LSB = micropython.const (0x02)

## The register address of the OUT_Y_MSB register in the MMA845x
OUT_Y_MSB = micropython.const (0x03)

## The register address of the OUT_Y_LSB register in the MMA845x
OUT_Y_LSB = micropython.const (0x04)

## The register address of the OUT_Z_MSB register in the MMA845x
OUT_Z_MSB = micropython.const (0x05)

## The register address of the OUT_Z_LSB register in the MMA845x
OUT_Z_LSB = micropython.const (0x06)

## The register address of the WHO_AM_I register in the MMA845x
WHO_AM_I = micropython.const (0x0D)

## The register address of the DATA_CFG_REG register in the MMA845x which is
#  used to set the measurement range to +/-2g, +/-4g, or +/-8g
XYZ_DATA_CFG = micropython.const (0x0E)

## The register address of the CTRL_REG1 register in the MMA845x
CTRL_REG1 = micropython.const (0x2A)

## The register address of the CTRL_REG2 register in the MMA845x
CTRL_REG2 = micropython.const (0x2B)

## The register address of the CTRL_REG3 register in the MMA845x
CTRL_REG3 = micropython.const (0x2C)

## The register address of the CTRL_REG4 register in the MMA845x
CTRL_REG4 = micropython.const (0x2D)

## The register address of the CTRL_REG5 register in the MMA845x
CTRL_REG5 = micropython.const (0x2E)

## Constant which sets acceleration measurement range to +/-2g
RANGE_2g = micropython.const (0)

## Constant which sets acceleration measurement range to +/-2g
RANGE_4g = micropython.const (1)

## Constant which sets acceleration measurement range to +/-2g
RANGE_8g = micropython.const (2)


class MMA845x:
    """ This class implements a simple driver for MMA8451 and MMA8452
    accelerometers. These inexpensive phone accelerometers talk to the CPU 
    over I<sup>2</sup>C. Only basic functionality is supported: 
    * The device can be switched from standby mode to active mode and back
    * Readings from all three axes can be taken in A/D bits or in g's
    * The range can be set to +/-2g, +/-4g, or +/-8g

    There are many other functions supported by the accelerometers which could 
    be added by someone with too much time on her or his hands :P 
    
    An example of how to use this driver follows.  It's a good idea to 
    instantiate the I<sup>2</sup>C driver separately and pass a reference to it
    to the accelerometer constructor, as the I<sup>2</sup>C driver can then be
    used to talk to other devices on the bus:
    @code
    i2c = pyb.I2C (1, pyb.I2C.MASTER, baudrate = 100000)
    mma = mma845x.MMA845x (i2c, 29)
    mma.active ()
    all3 = mma.get_accels ()       # Gets a tuple containing (ax, ay, az)
    just1 = mma.get_ax ()          # Gets X acceleration only
    @endcode 
    The example code works for an MMA8452 on a SparkFun<sup>TM</sup> breakout
    board. """

    def __init__ (self, i2c, address, accel_range = 0):
        """ Initialize an MMA845x driver on the given I<sup>2</sup>C bus. The 
        I<sup>2</sup>C bus object must have already been initialized, as we're
        going to use it to get the accelerometer's WHO_AM_I code right away. 
        @param i2c An I<sup>2</sup>C bus already set up in MicroPython
        @param address The address of the accelerometer on the I<sup>2</sup>C
            bus 
        @param accel_range The range of accelerations to measure; it must be
            either @c RANGE_2g, @c RANGE_4g, or @c RANGE_8g (default: 2g)
        """

        self._i2c = i2c
        self._addr = address

        # Request the WHO_AM_I device ID byte from the accelerometer
        self._dev_id = ord (i2c.mem_read (1, address, WHO_AM_I))

        if self._dev_id == 0x1A or self._dev_id == 0x2A:
            self._works = True
        else:
            self._works = False
            raise ValueError ('Unknown accelerometer device ID ' 
                + str (self._dev_id) + ' at I2C address ' + address)

        # Ensure the accelerometer is in standby mode so we can configure it
        self.standby ()

        # Set the acceleration range to the given one if it's legal
        self.set_range (accel_range)

        # This pre-allocated item holds data to be returned by _get_accel()
        self._raw_data = b'\x00\x00'


    def active (self):
        """ Put the MMA845x into active mode so that it takes data. In active
        mode, the accelerometer's settings can't be messed with. Active mode
        is set by setting the @c ACTIVE bit in register @c CTRL_REG1 to one.
        """

        if self._works:
            reg1 = ord (self._i2c.mem_read (1, self._addr, CTRL_REG1))
            reg1 |= 0x01
            self._i2c.mem_write (chr (reg1), self._addr, CTRL_REG1)


    def standby (self):
        """ Put the MMA845x into standby mode so its settings can be changed.
        No data will be taken in standby mode, so before measurements are to
        be made, one must call @c active(). """

        if self._works:
            reg1 = ord (self._i2c.mem_read (1, self._addr, CTRL_REG1))
            reg1 &= ~0x01
            self._i2c.mem_write (chr (reg1 & 0xFF), self._addr, CTRL_REG1)


    def set_range (self, new_range):
        """ Set the measurement range for the accelerometer. The range must be
        one of @c RANGE_2g, @c RANGE_4g, or @c RANGE_8g. This operation will
        only work if the accelerometer is in standby mode. 
        @param new_range The acceleration measurement range to be set """

        # Make sure the range variable is valid; if not, raise hackles
        if new_range < RANGE_2g or new_range > RANGE_8g:
            raise ValueError ('Invalid range for MMA845x: ' + str (new_range))
        else:
            # Make sure there's a working accelerometer present
            if self._works:

                # If in active mode, set it inactive
                actv = ord (self._i2c.mem_read (1, self._addr, CTRL_REG1)) \
                       & 0x01
                if actv:
                    self.standby ()
    
                # Now we can set the range
                self._range = new_range
                self._i2c.mem_write (new_range, self._addr, XYZ_DATA_CFG)
    
                # If accelerometer was active, re-activate it
                if actv:
                    self.active ()


    def _get_accel (self, MSB_reg, raw_data = bytearray (2)):
        """ Get an acceleration from the accelerometer and return it. The
        acceleration can be in the X, Y, or Z direction depending on the
        address of the registers from which it is retreived. 
        @param MSB_reg The address of the acceleration MSB register; the LSB
            will be in the next higher address
        @return The measured acceleration in A/D conversion bits """

        # Make sure there's a working accelerometer present
        if self._works:
            # Read the two registers with the MSB and LSB of acceleration
            self._i2c.mem_read (raw_data, self._addr, MSB_reg)

            # Convert the bytes into a usable integer
            raw_data = (raw_data[0] << 8) + raw_data[1]
            if raw_data > 32767:
                raw_data -= 65536

            return raw_data
        else:
            return 0


    def get_ax_bits (self):
        """ Get the X acceleration from the accelerometer in A/D bits and 
        return it.
        @return The measured X acceleration in A/D conversion bits """

        return self._get_accel (OUT_X_MSB)


    def get_ay_bits (self):
        """ Get the Y acceleration from the accelerometer in A/D bits and 
        return it.
        @return The measured Y acceleration in A/D conversion bits """

        return self._get_accel (OUT_Y_MSB)


    def get_az_bits (self):
        """ Get the Z acceleration from the accelerometer in A/D bits and 
        return it.
        @return The measured Z acceleration in A/D conversion bits """

        return self._get_accel (OUT_Z_MSB)


    def get_ax (self):
        """ Get the X acceleration from the accelerometer in g's, assuming
        that the accelerometer was correctly calibrated at the factory.
        @return The measured X acceleration in g's """

        return self.bits_to_g (self._get_accel (OUT_X_MSB))


    def get_ay (self):
        """ Get the Y acceleration from the accelerometer in g's, assuming
        that the accelerometer was correctly calibrated at the factory. The
        measurement is adjusted for the range (2g, 4g, or 8g) setting.
        @return The measured Y acceleration in g's """

        return self.bits_to_g (self._get_accel (OUT_Y_MSB))


    def get_az (self):
        """ Get the Z acceleration from the accelerometer in g's, assuming
        that the accelerometer was correctly calibrated at the factory. The
        measurement is adjusted for the range (2g, 4g, or 8g) setting.
        @return The measured Z acceleration in g's """

        return self.bits_to_g (self._get_accel (OUT_Z_MSB))


    def get_accels (self):
        """ Get all three accelerations from the MMA845x accelerometer. The
        measurement is adjusted for the range (2g, 4g, or 8g) setting.
        @return A tuple containing the X, Y, and Z accelerations in g's """

        return (self.get_ax (), self.get_ay (), self.get_az ())


    def bits_to_g (self, bits):
        ''' Scale a raw A/D reading to give g's of acceleration. This method
        might need to be called separately from taking data, for example if the
        data is taken in an interrupt service routine where floating point math
        should not be done.
        @param bits The integer from the accelerometer's A/D converter
        @return A factory calibrated acceleration in g's '''

        return bits * 2 ** (self._range + 1) / 32767.0


    def __repr__ (self):
        """ 'Convert' The MMA845x accelerometer to a string. The string 
        contains information about the configuration and status of the
        accelerometer. 
        @return A string containing diagnostic information """

        if not self._works:
            return ('No working MMA845x at I2C address ' + str (self._addr))
        else:
            reg1 = ord (self._i2c.mem_read (1, self._addr, CTRL_REG1))
            diag_str = 'MMA845' + str (self._dev_id >> 4) \
                + ': I2C address ' + hex (self._addr) \
                + ', Range=' + str (2 ** (self._range + 1)) + 'g, Mode='
            diag_str += 'active' if reg1 & 0x01 else 'standby'

            return diag_str



