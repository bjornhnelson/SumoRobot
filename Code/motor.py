''' @file motor.py
This file contains the MotorDriver class. '''

import pyb

class MotorDriver:
    ''' This class implements a motor driver for the
    ME405 board. '''

    def __init__ (self, Pin1, Pin2, Pin3, TimerNum):
        ''' Creates a motor driver by initializing GPIO.
        pins and turning the motor off for safety. 
        @param Pin1 The motor pin that uses timer channel 1
        @param Pin2 The motor pin that uses timer channel 2
        @param Pin3 The EN/OCD pin for the chosen motor pins
        @param TimerNum The timer channel that the motor pins use
        '''
        
        #print ('Creating a motor driver')
        self.pinEN = pyb.Pin(Pin3, pyb.Pin.OUT_PP) # set as output
        self.pinEN.high() # enable motor
        self.pin2 = pyb.Pin(Pin2, pyb.Pin.OUT_PP) # set as output
        self.pin1 = pyb.Pin(Pin1, pyb.Pin.OUT_PP) # set as output
        self.timer = pyb.Timer(TimerNum, freq=30000) # initialize timer for PWM

    def set_duty_cycle (self, level):
        ''' This method sets the duty cycle to be sent
        to the motor to the given level. Positive values
        cause torque in one direction, negative values
        in the opposite direction.
        @param level A signed integer holding the duty
        cycle of the voltage sent to the motor '''
        
        #print ('Setting duty cycle to ' + str (level))
        
        if level >= 0:
            self.pin2.low()
            ch1 = self.timer.channel(1, pyb.Timer.PWM, pin=self.pin1) # ch1 for pin1
            ch1.pulse_width_percent(level) # pin1 PWM
        else:
            self.pin1.low()
            ch2 = self.timer.channel(2, pyb.Timer.PWM, pin=self.pin2) # ch2 for pin2
            ch2.pulse_width_percent(level * -1) # pin2 PWM

