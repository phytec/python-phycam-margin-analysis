PYTHON phyCAM MARGIN ANALYSIS
=======================

Maintainer: Dirk Bender

responsible person: Benedikt Feldmann

status of the project: inactive, proprietary

type of the project: standalone

link to the documentation in confluece: 
https://wiki.phytec.com/display/~Feldmann/phyCAM-L+Margin+Analysis

Prerequisites and dependencies: Python3 capable board, SMBUS library


DESCRIPTION
#####
This tool is intended for checking the signal quality on a phyCAM-L coax connection.
The tool is based on the evaluation of an eye diagram. 
The user can determine the signal quality of the digital data transmission 
of a specific coaxial connection between phyCAM-L and VZ-018 module.

The use of this tool requires a Python3 capable board and the SMBUS library, 
which must be implemented on the BSP.


SETUP
#####
Connect the VZ-018 module to the i.MX 8M Plus board via phyCam-M interface.
Connect the coxial cable to be tested to port 0 of the VZ-018 module.
Attach the coxial cable end to phyCam-L module.
Reset the VZ-018 module.

USAGE
#####
This tool has different modes and required/optional arguments.


BUS address
****
Enter the BUS address of the connected phyCAM-M interface on the board.

From here on you can now choose between different optionally required values and arguments:

Digital Reset
****
Before starting the Margin Analysis test you can make a final digital reset 
including the registers.

Colored Map
****
Choose a colored or black and white graph output.

Dwell time
****
Wait until the next eye diagram area is scanned. 0.9 seconds is the default value.

Lock runs
****
Number of times an eye diagram area is sampled. 10 times is the default value.

Lock time
****
The time between initialization and evaluation of an eye diagram area 
during a lock run. 0.1 Seconds is the standard value.

Strobe/EQ Position
****
Limiting the scanning range in order not to scan the complete eye.

Clock/Data delay
****
Shifting the scanning range


RESULT
####

In the terminal, there is both a graphical and a percentage output of the scan.
A decision is made whether the cable has passed the quality test: 
For this, a 4 x 2 rectangle of the map must be completely permissible(green = 1.0) and 
at least three lines of the map must have at least four completely permissible 
eye diagram areas(green = 1.0) lined up next to each other.

Also there is a summary of the run in the ma_lock_result.txt file.


LICENSE:
####
???
