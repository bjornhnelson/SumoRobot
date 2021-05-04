''' @file main.py

    @summary This code runs the sumo robot.
    
    @author Jacob Rodriguez, Bjorn Nelson
'''

import pyb
import utime
import machine
import task_share
import cotask
import motor
import controller
import mma845x

from micropython import alloc_emergency_exception_buf
alloc_emergency_exception_buf (200)


def readIR():
    ''' This function parses data from an IR signal to detect a start 
    or stop button keypress. '''
    times = []
    cur = 0
    nextT = 0
    nextT2 = 0
    sig_start = False
    while True:
        if data.any():
            # print("The length is: " + str(len(times)))
            # print("There is data: " + str(data.num_in()))

            if cur == 0:
                cur = data.get()
            else:
                cur = nextT2

            if data.num_in() >= 2:
                nextT = data.get()
                nextT2 = data.get()
                diff1 = utime.ticks_diff(nextT, cur)
                diff2 = utime.ticks_diff(nextT2, nextT)

                if diff1 > 5000:
                    if diff2 > 4000 and diff2 < 5000:
                        # A leading pulse is detected
                        sig_start = True
                        times = []
                    elif diff2 < 4000 and diff2 > 2000:
                        # A repeat signal is detected
                        pass
                elif sig_start:
                    # Decoding the signal pulses into bits
                    if (2*diff1) > diff2:
                        times.append(0)
                    else:
                        times.append(1)

        if len(times) >= 32 and sig_start:
            times.reverse()
            com = times[8:16]
            word = ''
            for j in com:
                word += str(j)
            #print(word)

            if 12 == int(word, 2):
                command.put(1)
                #print("START COMMAND")
            else :
                command.put(0)
                #print("STOP COMMAND")

            times = []

        yield(0)


def getDistance():
    ''' This function reads data from the ultrasonic sensor and saves it in the dist share. '''
    while True:
        pinTrig.high()
        pinTrig.low()
        pulseTime = machine.time_pulse_us(pinEcho, 1)
        dist_cm = (pulseTime / 2) / 29  # microseconds to cm
        dist.put(dist_cm)
        #print("Distance: " + str(dist_cm))
        yield(0)


def getOptical():
    ''' Detects if there is a white line to stop motion. '''

    sensor = pyb.ADC(pinOptical)
    while True:
        val_f = sensor.read()
        #print("ADC: " + str(val_f))
        if val_f < 3000: # white line in front
            edge.put(1)
        yield(0)


def getAccelX():
    ''' This function reads data from the accelerometer and saves it in the accel share. '''

    mma = mma845x.MMA845x(i2c, 29) # i2c address 29
    mma.active() # activate sensor
    while True:
        x = mma.get_ax() # get acceleration in x direction
        accel.put(x) # put value in share
        yield(0)


def Brain():
    ''' This function processes the data from the sensors and tells the motors what to do. '''

    command.put(0)
    ir_count = 40
    dist.put(150)
    while True:
        if command.get() == 1: # start button pushed on IR remote

            # edge detection logic
            if edge.get() == 1: # near an edge
                if ir_count != 1: # back up
                    direction_R.put(2)
                    direction_L.put(2)
                    ir_count -= 1
                else: # done backing up
                    ir_count = 40
                    edge.put(0)

            # no opponent found logic
            elif dist.get() > 20:
                # Turn right
                direction_R.put(2)
                direction_L.put(1)

            # collision logic
            elif abs(accel.get()) > 0.07:
                # Turn left
                direction_R.put(1)
                direction_L.put(2)

            # opponent found logic
            else:
                # move forward
                direction_R.put(1)
                direction_L.put(1)

        else: # other button pushed on IR remote
            # need to stop motors and halt motion
            direction_R.put(0)
            direction_L.put(0)

        yield(0)


def motor_R():
    ''' This function controls the right motor. '''

    # Create the objects to control it
    Mo_R = motor.MotorDriver(pyb.Pin.board.PB4, pyb.Pin.board.PB5, pyb.Pin.board.PA10, 3)
    Con_R = controller.Controller(.1, 10000, pyb.Pin.board.PC6, pyb.Pin.board.PC7, 8)
    while True:
        effort = -Con_R.run(direction_R.get())
        Mo_R.set_duty_cycle(effort)
        yield(0)


def motor_L():
    ''' This function controls the left motor. '''

    # Create the objects to control it
    Mo_L = motor.MotorDriver(pyb.Pin.board.PA0, pyb.Pin.board.PA1, pyb.Pin.board.PC1, 5)
    Con_L = controller.Controller(.1, 10000, pyb.Pin.board.PB6, pyb.Pin.board.PB7, 4)
    while True:
        effort = Con_L.run(direction_L.get())
        Mo_L.set_duty_cycle(effort)
        yield(0)


def interrupt1(t):
    ''' The interrupt function: when a signal edge is detected this
    will save the timestamp associated with that edge. '''
    if not data.full():
        data.put(utime.ticks_us(), in_ISR=True)


if __name__ == "__main__":
    ''' The main function, which stores the shares and queues, manages the tasks, and runs the scheduler. '''

    # Pin Definitions

    # Ultrasonic sensor pins
    pinTrig = pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.OUT_PP)
    pinEcho = pyb.Pin(pyb.Pin.board.PA9, pyb.Pin.IN)

    # Edge detection sensor pin
    pinOptical = pyb.Pin(pyb.Pin.board.PC0, pyb.Pin.IN)

    # Accelerometer i2c pins
    i2c = pyb.I2C(1, pyb.I2C.MASTER)

    # IR sensor pin and setup
    tim1 = pyb.Timer(1, period=65535, prescaler=79)
    pinIR = pyb.Pin(pyb.Pin.board.PA8, pyb.Pin.IN)
    ch1 = tim1.channel(1, mode=pyb.Timer.IC, pin=pinIR, polarity=pyb.Timer.BOTH)
    ch1.callback(interrupt1)

    # Creating shares and queues to allow data to pass between tasks

    # The Shares

    # The share named dist will be used to tell the brain task how far the
    # opponent is from the bot, will be larger than the size of the ring or
    # zero when there is no opponent in front of the bot.
    dist = task_share.Share('f', thread_protect=False, name='dist')

    # This share will be set by the brain task and will tell the right motor
    # which direction to move in. It will be set to 0 to stop, 1 for forward,
    # and 2 for backwards.
    direction_R = task_share.Share('I', thread_protect=False, name='dir_r')

    # This share will be set by the brain task and will tell the left motor
    # which direction to move in. It will be set to 0 to stop, 1 for forward,
    # and 2 for backwards.
    direction_L = task_share.Share('I', thread_protect=False, name='dir_l')

    # The accel share communicates to the brain what kind of acceleration the
    # bot is experiencing and will be used to determine if there has been a
    # collision with another bot.
    accel = task_share.Share('f', thread_protect=False, name='accel')

    # This share will be used to indicate when the robot should start operating
    # when a button on the IR remote is pressed. It will be set to 1 when the
    # start button is pressed and set to 0 when any other button is pressed.
    command = task_share.Share('I', thread_protect=False, name='command')

    # This share will be used by both the edge detection task and the brain
    # task. The value 0 corresponds to no edge and 1 for when an edge is
    # detected by sensor.
    edge = task_share.Share('I', thread_protect=False, name='edges')

    # The Queues

    # This queue is used to save the IR signal timestamps while in the ISR.
    data = task_share.Queue('I', 136, thread_protect=False, overwrite=True, name="Data")

    # Creating the tasks for the sumo bot
    Read_IR = cotask.Task(readIR, name='Read_IR', priority=5, period=30)
    Brain_task = cotask.Task(Brain, name='Brain_task', priority=4, period=100)
    Motor_R = cotask.Task(motor_R, name="Motor_R", priority=4, period=3)
    Motor_L = cotask.Task(motor_L, name="Motor_L", priority=4, period=3)
    Ultrasonic = cotask.Task(getDistance, name="Ultrasonic", priority=2, period=70)
    Edge_det = cotask.Task(getOptical, name="Edge_det", priority=4, period=50)
    Accel = cotask.Task(getAccelX, name="Accel", priority=2, period=50)

    # Appending the tasks to the task list run by the scheduler
    cotask.task_list.append(Read_IR)
    cotask.task_list.append(Brain_task)
    cotask.task_list.append(Ultrasonic)
    cotask.task_list.append(Edge_det)
    cotask.task_list.append(Accel)
    cotask.task_list.append(Motor_R)
    cotask.task_list.append(Motor_L)

    # Run the scheduler with the chosen scheduling algorithm. Quit if any
    # character is sent through the serial port
    vcp = pyb.USB_VCP ()
    while not vcp.any ():
        cotask.task_list.pri_sched ()

    # Empty the comm port buffer of the character(s) just pressed
    vcp.read ()
