# SumoRobot
Cal Poly Mechatronics Final Project, Winter 2020  

Video Demo: https://youtu.be/V-FPE-wgGrk  

![Robot Picture](/Images/robot.png)

## Introduction
Robot-sumo is a competition where two robots attempt to push each other outside of a circular arena. There are various classes of competitions that are held worldwide. To solve the associated engineering challenges, sensors are typically used to find the opponent and detect the arena edge and an angled blade is used to push the opponent. The target customer of the robot we designed is someone who wants to participate in an autonomous sumo robot competition but does not have experience with building mechatronics projects on their own.

The robots designed in ME 405 competed in an end of quarter class tournament in a 4 ft diameter black arena with a 2 in solid white border. Two white lines in the center were used as the start positions for the two robots, and a button on an IR remote was used to start each round of the competition. The robots competed in 3 minute rounds, with the robot closest to the center declared the winner if both robots remained in the arena the entire time.

In order to build a working robot, various mechanical, electrical, and software systems had to be integrated prior to the tournament. Our mechanical design was a 3D printed body with an open top that contained enclosures for all of the components. Two DC motors, two wheels, and a castor were used to facilitate movement. The electrical system consisted of the STM32L476 microcontroller, an ultrasonic sensor to find the opponent, an accelerometer to detect collisions, and an IR sensor to detect edges. The software system was written in Python and utilized a priority task scheduler to process data from the sensors and direct the motors in an appropriate way. The tasks were tested individually before they were integrated into the overall source code.

## Specifications
Table 1: Robot Specifications
![Robot Specifications](/Images/specifications.png)

The robot had to use the following components at a minimum.
- An ME405 board or equivalent microcontroller running MicroPython
- Two motors which supply torque to drive the SUMO bot
- At least one sensor measuring horizontal motion
- An opponent detection sensor
- A line detection sensor (or several)
- An infrared receiver reserved for start and stop commands from the referee

## Design Development
Considering that the sumo bot must be able to function without human control besides the signal to activate and deactivate the system, the hardware and software must be designed and selected with that in mind. The bot needed to be able to sense the opponent bot in the arena and sense if it was going outside of the arena at any time.

### Brainstorming
The sumo bot needs to be able to sense parts of the arena and then make decisions based on what the sensors pick up. Therefore, the development process can be split into two parts: integrating the sensors and controlling the motors. Some online research was done on different mechanical and electrical components used in past sumo bot competitions, in order to choose the best sensors and motors for the project [1]. The data sheet for the STM32L476 microcontroller was also referenced to see which pins to use for different sensors [2]. 3.3 V sensors were prioritized because of compatibility with the microcontroller board.

During an early stage of developing the software and building the hardware, a motor was connected improperly and caused the Nucleo board to malfunction and require a replacement. To prevent this from happening again, we connected all of the other components and made the software print out what motion would be performed at a given time. This helped ensure that all the sensors were being read properly and that the data was processed correctly.

### Hardware Design
An ultrasonic sensor was used to find the opponent, since it has a wide field of view to detect objects in front of it. The sensor works by emitting a sound wave and waiting for the wave to be reflected, calculating the distance based on the wait time. The sensor required 4 connections, one for power, ground, echo and trig. The trigger pin was pulsed and the echo pin was monitored to calculate how far away an object was from the bot. Another sensor that we wanted to use to detect collisions was an accelerometer. This sensor can measure the acceleration in the x, y, and z directions at any point in time. It was connected to the board using the I2 C communications protocol, which required two wires for SCL and SDA, in addition to power and ground wires.

The sumo bot had two different IR sensors, which were used for different goals. The first sensor is a TSOP38438 IR receiver that was used to receive IR signals from a remote. This allowed the bot to know when to turn on or off depending on which button was pressed. This sensor needed to be placed in a location that would give it the most exposure to incoming signals while not being too exposed and at risk of being knocked off during competition. The second IR sensor was used to detect white lines around the edge of the arena. This sensor works by reading different values on black and white surfaces, due to the variance in the light reflectivity. Each of these IR sensors were connected to the board using power, ground, and an analog pin.

To move the bot we picked Micro Metal Geared motors for their low power consumption and small size, making the overall design for the bot smaller. This allowed us to utilize a smaller battery to power the motors, which also makes the bot lighter and more agile. An emergency stop button was also included to enable power to be cut to the motors at any time. Choosing the right wheels was only a matter of finding ones with the correct hole size for the motor shaft to go into. The sumo bot will need to be able to turn, so we decided to use a castor in the front that slides on the arena surface when the motors move in opposite directions. For simplicity, we used a 9 V battery to power the motors and a small phone charger battery to power the board over a USB cable. The overall system architecture showing all of the components is shown in Figure 1.

![System Architecture](/Images/system_architecture.png)
Figure 1: System Architecture

The housing for the system was 3D printed with thermoplastic. The housing included pockets for all of the components, and the top was left open to allow direct access to the components and minimize the overall weight. The design of the 3D printed enclosure is shown in Figure 2.

![CAD Model](/Images/cad_model.png)
Figure 2: Enclosure CAD Model

### Software Design
The software was written using MicroPython and its various libraries. The design of software for a mechatronics-based context was approached using the task methodology that was taught in class. Several existing modules were provided to us, including the implementation of a queue, share, and task scheduler. We also used an existing module to read accelerometer data [3].

The overall task diagram of the robot is shown in Figure 3. The command share stores a binary value indicating whether a remote keypress is the start command. The data queue stores the pattern of the IR signal. The dist share stores the distance away an obstacle is from the front of the robot. The accel share stores the acceleration along the x-axis. The edge share stores a binary value indicating whether the robot is near the edge of the arena. The dir_L and dir_R shares store values indicating the directions (forward, backward, stop) the left and right motors should turn.

![Task Diagram](/Images/task_diagram.png)
Figure 3: Task Diagram

The software as a whole runs the four tasks used to collect data from the sensors, then runs the Operate Brain task to process the data and determine the best response by the motors, and then uses the encoder class and motor driver class to actuate the motors. A software flowchart of the Operate Brain task is shown in Figure 4. This task controls how the robot moves based on sensor input and is the core logic of the programming.

![Task Diagram](/Images/software_flowchart.png)
Figure 3: Software Flowchart

### Testing
During development, we first tested each of the sensors separately to get them functioning before everything was combined together. From testing the ultrasonic sensor, we discovered that the maximum range was about 60 cm in front of the bot; the sensor returned a distance of 20 cm after this point, which could be a big issue when trying to find another bot in the sumo ring. The code was adjusted so that any value less than 20 cm would be recognized as an opponent bot, which limited the vision but prevented bad readings. The IR white line detector was working well up to the day of the competition. It would return values above 3000 when pointed toward a darker surface and return values below 300 when pointed at a white surface. The IR receiver for the remote signals worked consistently, as long as the remote was not too far from the sensor.

## Results
Our robot performed well overall, winning the first round and losing the second round in the competition. In the first round, reliability of the system was key. The other team’s IR receiver was not placed in an optimal position, so the opponent robot took a while to respond or did not respond at all. In addition, our motors produced sufficient torque to push a larger robot out of the arena, even though they were small in size. In the second round, our edge detection sensor did not work properly and the other robot had a better search strategy to find their opponent.

We learned many things from doing this project. One important lesson is the importance of time management, since integration often takes longer than expected. Starting earlier, we could have fine tuned the sensors and made the system run more smoothly than it did. Another important skill we learned is design of the system or software before going to build it or code it. The initial design stages provide a framework for a successful project and can have a significantly positive impact at the end of the project or if any issues arise during the development stages.

In future development, the opponent search strategy can be improved in software. Currently, no random values are used to determine which direction the robot turns if an opponent is not found. There are also different navigation algorithms (such as A*) that could be implemented to find the opponent robot more quickly. In addition, the software could have additional code to ignore the white starting lines. Finally, measured acceleration in the y-direction could be incorporated into the software, so motor control after a collision is dependent on the exact location of a collision.

## Bill of Materials
The total cost for the components of this project is $87.34. The individual prices of the items are shown in Table 2. Provided items, such as the microcontroller and motor driver boards and 3D printing materials, were not factored into the bill of materials.

Table 2: Project Bill of Materials
![Project Bill of Materials](/Images/bom.png)

## References
[1] “Arduino Sumo Robot”, Instructables, https://www.instructables.com/id/How-to-MakeArduino-Sumo-Robot.

[2] “STM32L476xx Data Sheet”, https://www.st.com/resource/en/datasheet/stm32l476je.pdf.

[3] Ridgely, John. “Source Code for MMA8451 Accelerometer”, http://wind.calpoly.edu/ME405/doc/classmma845x__shell_1_1MMA845x.html#details.
