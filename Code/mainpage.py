## @file mainpage.py
# @author Jacob Rodriguez 
# @author Bjorn Nelson 
# @mainpage
#
# @section intro Introduction
# The purpose of this code is to run the sumo robot in the competition.
# The goal of the competition is to push the opponent outside of the
# circular arena or be the robot closest to the center of the arena at
# the end of the round.
#
# @section usage Usage
# The main file uses the other modules automatically, so the only program
# that needs to be run is main.py. Once it runs, the program waits for the
# 1 button to be pressed on the IR remote to indicate startup. After this,
# the robot reads data from the ultrasonic sensor to find the opponent,
# data from the accelerometer to detect collisions, and data from the IR
# optical sensor to detect the edge of the arena. This data is analyzed to
# direct the motors in the appropriate way.
#
# @section testing Testing
# The sensors were individually tested and then integrated into the overall
# source code.
# 
# @section bugs Bugs & Limitations
# The sensors do not produce exact measurements and may need to be
# re-calibrated. In addition, the navigation system could be improved to
# detect and respond to more complex in-game scenarios.
# 
# @section loc Location
# Mercurial path to source code files: mecha04/FinalProject
#