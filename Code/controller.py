''' @file controller.py
This file contains the Controller class. '''

import pyb
import task_share
import utime


class Controller:
    ''' This class implements closed-loop proportional 
    control for the ME405 board. '''

    def __init__(self, setGain, setPoint, pin1, pin2, timNum):
        ''' Initializes the pins and timer.
        @param setGain A float storing the gain value
        @param setPoint An int storing the set point value
        @param pin1 A Pin object for timer channel 1
        @param pin2 A Pin object for timer channel 2
        @param timNum An int holding the timer number '''
        self.gain = setGain
        self.setPoint = setPoint
        self.pinA = pyb.Pin(pin1, pyb.Pin.IN)
        self.pinB = pyb.Pin(pin2, pyb.Pin.IN)
        self.timer = pyb.Timer(timNum)
        self.timer.init(prescaler=0, period=65535) # initialize timer
        self.timer.channel(1, pyb.Timer.ENC_AB, pin=self.pinA) # initialize ch1
        self.timer.channel(2, pyb.Timer.ENC_AB, pin=self.pinB) # initialize ch2
        
        # set all tick values to 0
        self.curTicks = 0 # An integer to save tick value from counter()
        self.pastTicks = 0 # An integer to save previous value of curTicks
        self.timer.counter(0)
        self.timeRef = utime.ticks_ms()
        
    def run(self, direction):
        ''' Calculates the actuation value to power the motor. '''

        self.pastTicks = self.curTicks # save previous tick value
        self.curTicks = self.timer.counter() # get new tick value
        #print("CurTicks: " + str(self.curTicks) + " PastTicks: " + str(self.pastTicks))
        
        # positional difference between last read and current read
        distance = self.curTicks - self.pastTicks
        
        if direction == 1:
            # wants to move forward
            actuatSig = 65
        elif direction == 0:
            # set the motor to stop moving
            actuatSig = 0
        elif direction == 2:
            # wants to move backward
            actuatSig = -65
        
        return actuatSig
        
    def setSetPoint(self, setPoint):
        ''' Set the desired setPoint for the controller. 
        @param setPoint The desired location '''
        self.setPoint = setPoint
        
    def setGain(self, setGain):
        ''' Changes the proportional gain for the controller. 
        @param setGain The new proportional gain value '''
        self.gain = setGain
        
    def reset(self):
        ''' Resets the values read in the encoder for the next test. '''
        self.curTicks = 0 # An integer to save tick value from counter()
        self.pastTicks = 0 # An integer to save previous value of curTicks
        self.timer.counter(0)
        self.timeRef = utime.ticks_ms()
    
    def clearTime(self):
        ''' Sets the reference time. '''
        self.timeRef = utime.ticks_ms()
