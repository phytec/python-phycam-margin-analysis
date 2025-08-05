======================
phyCAM MARGIN ANALYSIS
======================

Link to the main documentation :
https://wiki.phytec.com/pages/releaseview.action?pageId=446169306


DESCRIPTION
###########
This tool is intended for checking the signal quality on a phyCAM-L coax connection.
The tool is based on the evaluation of an eye diagram.
The user can determine the signal quality of the digital data transmission
of a specific coaxial connection between phyCAM-L and VZ-018 module.

The prerequisites and dependencies for the use of this tool are a Python3-capable
Linux image and the SMBUS library.


SETUP
#####
Connect the VZ-018 module to the PHYTEC board via phyCam-M interface.
Connect the coaxial cable to be tested to a port of the VZ-018 module.
Attach the coaxial cable end to phyCam-L module.
Reset the VZ-018 module.


USAGE
#####
This tool has different modes and required/optional arguments.

BUS address
    Enter the BUS address of the connected phyCAM-M interface on the board.

From here on you can now choose between different optionally required values and arguments:

Port number
    FPD-Link III port the phyCam-L module is connected to. Defaults to port 0 (just press enter).

Digital Reset
    Before starting the Margin Analysis test, you can make a final digital reset
    including the registers. Useful if the camera was in use before, i.e. enabled via overlay.

Colored Map
    Choose a colored or black and white graph output.

Dwell time
    Wait until the next eye diagram area is scanned. 0.9 seconds is the default value.

Lock runs
    Number of times an eye diagram area is sampled. 10 times is the default value.

Lock time
    The time between initialization and evaluation of an eye diagram area
    during a lock run. 0.1 Seconds is the standard value.

Strobe/EQ Position
    Limiting the scanning range in order not to scan the complete eye.

Clock/Data delay
    Shifting the scanning range


RESULT
######

In the terminal, there is both a graphical and a percentage output of the scan.
A decision is made whether the cable has passed the quality test:
For this, a 4 x 2 rectangle of the map must be completely permissible (green = 1.0) and
at least three lines of the map must have at least four completely permissible
eye diagram areas (green = 1.0) lined up next to each other.

Additionally, there is a summary of the run in the ma_lock_result.txt file.


LICENSE:
########

The code is released unter the MIT license, see COPYING.MIT.
