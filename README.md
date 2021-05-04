# SumoRobot
Cal Poly Mechatronics Final Project, Winter 2020  

Video Demo: https://youtu.be/V-FPE-wgGrk  

![Robot Picture](/images/robot.jpg)

## Introduction
Robot-sumo is a competition where two robots attempt to push each other outside of a circular arena. There are various classes of competitions that are held worldwide. To solve the associated engineering challenges, sensors are typically used to find the opponent and detect the arena edge and an angled blade is used to push the opponent. The target customer of the robot we designed is someone who wants to participate in an autonomous sumo robot competition but does not have experience with building mechatronics projects on their own.

The robots designed in ME 405 competed in an end of quarter class tournament in a 4 ft diameter black arena with a 2 in solid white border. Two white lines in the center were used as the start positions for the two robots, and a button on an IR remote was used to start each round of the competition. The robots competed in 3 minute rounds, with the robot closest to the center declared the winner if both robots remained in the arena the entire time.

In order to build a working robot, various mechanical, electrical, and software systems had to be integrated prior to the tournament. Our mechanical design was a 3D printed body with an open top that contained enclosures for all of the components. Two DC motors, two wheels, and a castor were used to facilitate movement. The electrical system consisted of the STM32L476 microcontroller, an ultrasonic sensor to find the opponent, an accelerometer to detect collisions, and an IR sensor to detect edges. The software system was written in Python and utilized a priority task scheduler to process data from the sensors and direct the motors in an appropriate way. The tasks were tested individually before they were integrated into the overall source code.
