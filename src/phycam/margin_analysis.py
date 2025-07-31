""" phycam margin_analysis
Program to calibrate phyCAM hardware.
Version: 0.15
Author: Benedikt Feldmann <B.Feldmann@phytec.de>
Maintainer: Dirk Bender <D.bender@phytec.de>

The code is based on the Texas Instruments Analog LaunchPAD DS90UB954
with permission for redistribution in an MIT compatible way, 07-2021.

SPDX-License-Identifier: MIT
Copyright: (C) 2021 PHYTEC Messtechnik GmbH
"""

import time
from smbus2 import SMBus


class I2C:
    """I2C commands with SMBUS"""
    def __init__(self, dev_address):
        self.i2c = dev_address # i2c bus: J8.3 (GPIO2) as SDA,
                                            # J8.5 (GPIO3) as SCL

    def detect(self):
        """tries to scan the I2C bus for devices"""
        # output: table with the list of detected devices on the specified bus
        # inspired by shell command "i2cdetect -y 2"
        i2cbus = SMBus(self.i2c, force=True)
        print('     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f')
        for addr in range(0, 127, 16):
            lin = '{:02x}:'.format(addr)
            for i in range(0, 16):
                if addr + i < 3:
                    lin += '   '
                else:
                    try:
                        i2cbus.write_i2c_block_data(addr + i, 0, [])
                    except OSError:
                        lin += ' --'
                    else:
                        lin += ' {:02x}'.format(addr + i)
            print(lin)
        i2cbus.close()

    def read(self, addr, reg):
        """read register of the slave"""
        # returns a list of received data
        # inspired by shell command "i2cget"
        i2cbus = SMBus(self.i2c, force=True)
        i2cbus.read_byte_data(addr, reg)
        i2cbus.close()

    def write(self, addr, reg, data):
        """write register of the slave"""
        # inspired by shell command "i2cset"
        # no return value
        i2cbus = SMBus(self.i2c, force=True)
        i2cbus.write_byte_data(addr, reg, data)
        i2cbus.close()

class Bcolors():  # pylint: disable=too-few-public-methods
    """color for the characters"""
    OK = '\033[32m' #GREEN
    WARNING = '\033[33m' #YELLOW
    FAIL = '\033[31m' #RED
    RESET = '\033[0m' #RESET COLOR


class MarginRequest():
    """question for optional parameter request"""
    def __init__(self, question):
        self.question = question
        self.variable = 0

    def yes_no(self):
        """input: yes or no"""
        while True:
            print()
            print(self.question)
            ma_input = input()
            if (str(ma_input) == "y" or str(ma_input) == "Y" or
                    str(ma_input) == "j" or str(ma_input) == "Yes" or
                    str(ma_input) == "yes"):
                self.variable = 1
                break
            if (str(ma_input) == "n" or str(ma_input) == "N" or
                    str(ma_input) == "no" or str(ma_input) == "No" or
                    str(ma_input) == "NO"):
                self.variable = 0
                break
            print("Incorrect input, please try again!")
        return self.variable

    @staticmethod
    def color_output(s_c_output, eq_value):
        """map output"""
        if s_c_output == 1:
            if eq_value == 1:
                print(Bcolors.OK + "▇▇" + Bcolors.RESET, end=" ")
                #sys.stdout.write(Bcolors.OK + "▇▇ " + Bcolors.RESET)
            elif eq_value == 0:
                print(Bcolors.FAIL + "▇▇" + Bcolors.RESET, end=" ")
                #sys.stdout.write(Bcolors.FAIL + "▇▇ " + Bcolors.RESET)
            else:
                print(Bcolors.WARNING + "▇▇" + Bcolors.RESET, end=" ")
                #sys.stdout.write(Bcolors.WARNING + "▇▇ " + Bcolors.RESET)
        if s_c_output == 0:
            if eq_value == 1:
                #print("##", end=" ")
                print("██", end=" ")
            elif eq_value == 0:
                #print("  ", end=" ")
                print("--", end=" ")
            else:
                #print("--", end=" ")
                print("▒▒", end=" ") #7x lock status #7x lock status

    def output(self):
        """value return"""
        return self.variable


class MarginInput:
    """question for optional parameter input"""
    def __init__(self, article, what, variable):
        self.article = article
        self.what = what
        self.variable = variable

    def float_input(self, start, end):
        """range between and insert of float value"""
        while True:
            print("\nDo you want to set", self.article, self.what, "? (y/n)")
            ma_input = input()
            if (str(ma_input) == "y" or str(ma_input) == "Y" or
                    str(ma_input) == "j" or str(ma_input) == "Yes" or
                    str(ma_input) == "yes"):
                print()
                while True:
                    print("Enter a value between", start, "and", end, "(ms):")
                    variable = input()
                    try:
                        variable = float(variable)
                        if start <= variable <= end:
                            self.variable = variable / 1000
                            break
                        print("\nPlease try again!")
                    except ValueError:
                        print("\nPlease try again!")
                break
            if (str(ma_input) == "n" or str(ma_input) == "N" or
                    str(ma_input) == "no" or str(ma_input) == "No" or
                    str(ma_input) == "NO"):
                print("The", self.what, "value",
                      self.variable, "is set by default")
                break
            print("Incorrect input, please try again!")
        print("current", self.what, ": ", self.variable, "second(s)\n")
        return self.variable

    def int_input(self):
        """only a minimum value for the integer parameter"""
        while True:
            print("\nDo you want to set", self.article, self.what, "? (y/n)")
            ma_input = input()
            if (str(ma_input) == "y" or str(ma_input) == "Y" or
                    str(ma_input) == "j" or str(ma_input) == "Yes" or
                    str(ma_input) == "yes"):
                print()
                while True:
                    print("Enter an integer value greater than",
                          self.variable, ":")
                    variable = input()
                    try:
                        variable = int(variable)
                        if variable >= self.variable:
                            self.variable = variable
                            break
                        print("\nPlease try again!")
                    except ValueError:
                        print("\nPlease try again!")
                break
            if (str(ma_input) == "n" or str(ma_input) == "N" or
                    str(ma_input) == "no" or str(ma_input) == "No" or
                    str(ma_input) == "NO"):
                print("The", self.what, "value",
                      self.variable, "is set by default")
                break
            print("Incorrect input, please try again!")
        print("current", self.what, ": ", self.variable, "\n")
        return self.variable

    def output(self):
        """parameter return"""
        return self.variable




class MarginPosition:
    """optional map range"""
    def __init__(self, what):
        self.what = what
        self.begin_variable = 0
        self.end_variable = 14
        self.variable = 0

    def yes_no(self):
        """input: yes or no"""
        while True:
            print("\nDo you want to set", self.what, "? (y/n)")
            ma_input = input()
            if (str(ma_input) == "y" or str(ma_input) == "Y" or
                    str(ma_input) == "j" or str(ma_input) == "Yes" or
                    str(ma_input) == "yes"):
                print()
                self.variable = 1
                break
            if (str(ma_input) == "n" or str(ma_input) == "N" or
                    str(ma_input) == "no" or str(ma_input) == "No" or
                    str(ma_input) == "NO"):
                print("The", self.what, "start value", self.begin_variable,
                      "and", self.what, "end value",
                      self.end_variable, "is set by default.")
                self.variable = 0
                break
            print("Incorrect input, please try again!")
        return self.variable

    def output(self):
        """parameter return"""
        return self.variable

    def begin_end(self, start, end):
        """set map range integer values"""
        while True:
            print("Enter integer values from", start,
                  "to", end, ":")
            print(self.what, "Begin:")
            begin_variable = input()
            try:
                begin_variable = int(begin_variable)
                if start <= begin_variable <= end:
                    self.begin_variable = begin_variable
                    print(self.what, "End:")
                    end_variable = input()
                    try:
                        end_variable = int(end_variable)
                        if (start <= end_variable <= end and
                                begin_variable <= end_variable):
                            self.end_variable = end_variable
                            break
                        print()
                        print("Please try again! The values can not be equal!")
                    except ValueError:
                        print("\nPlease try again!")
                else:
                    print("\nPlease try again!")
            except ValueError:
                print("\nPlease try again!")
        return self.begin_variable, self.end_variable

    def begin(self):
        """return begin parameter of the map range"""
        return self.begin_variable

    def end(self):
        """return end parameter of the map range"""
        return self.end_variable


# Define registers and values from datasheet
I2C_ADDRESS_DS90UB954 = 0x3d #this is the default ID if id-pin is pulled high
I2C_ADDRESS_DS90UB953 = 0x30

REG_I2C_DEV_ID = 0x00
REG_RESET = 0x01
REG_PAR_ERR_THOLD_HI = 0x05
REG_PAR_ERR_THOLD_LO = 0x06
REG_RX_PORT_CTL = 0x0c
REG_AEQ_CTL1 = 0x42
REG_FPD3_CAP = 0x4a
REG_FPD3_PORT_SEL = 0x4c
REG_RX_PORT_STS1 = 0x4d
REG_RX_PORT_STS2 = 0x4e
REG_RX_PAR_ERR_LO = 0x56
REG_IND_ACC_CTL = 0xb0
REG_IND_ACC_ADDR = 0xb1
REG_IND_ACC_DATA = 0xb2
REG_FPD3_ENC_CTL = 0xba
REG_ADAPTIVE_EQ_BYPASS = 0xd4

IND_REG_OFF_STROBE_SET = 0x08

RX_PORT_CTL_RESERVED = 0x2 << 6 # bit 7:6 default to 0x2
RX_PORT_CTL_PORT0_EN = 1 << 0
RX_PORT_CTL_PORT1_EN = 1 << 1
RX_PORT_CTL_LOCK_SEL_SHIFT = 2

FPD3_PORT_SEL_RX_READ_PORT_SHIFT = 4

def main():
    """
    Main program function
    """

    date = time.strftime("%d.%m.%Y\ntime: %H:%M:%S\n", time.localtime())

    #MARGIN ANALYSIS Testversuch
    print("\n###########################################################")
    print("##################### MARGIN ANALYSIS #####################")
    print("###########################################################")
    print(f"date: {date}")


    #lock result file
    table = open("./ma_lock_result.txt", "w+", encoding="utf-8")
    table.write(f"date: {date}")
    table.write(",,,,,,,,LOCK-RESULT,,,,,,,,")
    table.write("\n")
    table.write(",,,,,,,,SP,,,,,,,,")
    table.write("\n")
    table.write("EQ,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14")

    #which Board
    while True:
        print("Which BUS address is assigned to the phyCAM-M interface?")
        which_bus = input()
        try:
            which_bus = int(which_bus)
            i2ctemp = SMBus(which_bus, force=True)  # Create a new I2C bus
            dev_id = i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_I2C_DEV_ID)
            # bit 0 id dev_id indicates if id is overwritten by register,
            # alternative id strappings or set by register not supported
            if which_bus >= 0 and (dev_id >> 1) == I2C_ADDRESS_DS90UB954:
                print("\tBUS-check: OK")
                i2ctemp.close()
                print("Which Port is the phyCAM-L interface connected to (enter for default)?")
                which_port = input()
                match which_port:
                    case "":
                        which_port = 0
                        print("\tTesting on default port 0")
                        break
                    case "0" | "1":
                        print(f"\tTesting on port {which_port}")
                        which_port = int(which_port)
                        break
                    case _:
                        print("\tIncorrect Port input, please try again!")
            else:
                print("\tIncorrect BUS address input, please try again!")
                i2ctemp.close()
        except ValueError:
            print("\tIncorrect input, please insert an integer value!")
        except FileNotFoundError:
            print("\tBus does not exist, please try again!")
    i2ctemp.close()
    print()


    i2c = I2C(which_bus)
    #i2c.detect()


    #do a final digital reset including registers if selected
    digital_reset = MarginRequest("Do you want to do a final " +
                                  "digital reset including registers " +
                                  "before starting the test? (y/n)")
    digital_reset.yes_no()
    if digital_reset.output() == 1:
        i2c.write(I2C_ADDRESS_DS90UB954, REG_RESET, 0x02)
    else:
        print("\rNo final digital reset!")
    print()

    #set RX_PORT_CTL register
    i2c.write(I2C_ADDRESS_DS90UB954, REG_RX_PORT_CTL, RX_PORT_CTL_RESERVED
                                                    | RX_PORT_CTL_PORT0_EN
                                                    | RX_PORT_CTL_PORT1_EN
                                                    | which_port << RX_PORT_CTL_LOCK_SEL_SHIFT)
    #Port 0 and Port1 Receiver enabled, Port x Receiver Lock
    time.sleep(0.1)
    #set Read/Write Enable for RX port x registers in FPD3_PORT_SEL register
    rx_write_port = 0x01 << which_port
    rx_read_port = which_port << FPD3_PORT_SEL_RX_READ_PORT_SHIFT
    i2c.write(I2C_ADDRESS_DS90UB954, REG_FPD3_PORT_SEL, rx_write_port | rx_read_port)
    time.sleep(0.1)

    # prepare indirect register access
    # choose FPD-Link III RX Port x Reserved Registers: Test and Debug registers
    i2c.write(I2C_ADDRESS_DS90UB954, REG_IND_ACC_CTL, 0x01 << (2 + which_port))
    time.sleep(0.1)
    # choose STROBE_SET (@offset 8)
    i2c.write(I2C_ADDRESS_DS90UB954, REG_IND_ACC_ADDR, IND_REG_OFF_STROBE_SET)
    time.sleep(0.1)
    # values will be written to REG_IND_ACC_DATA later in the test loops!

    # configure AEQ_CTL register: Disable SFILTER adaption with AEQ
    i2c.write(I2C_ADDRESS_DS90UB954, REG_AEQ_CTL1, 0x70)
    #AEQ Error Control: [6] FPD-Link III clock errors,
    #                   [5] Packet encoding errors, [4] Parity errors
    time.sleep(0.1)
    # set AEQ Bypass register: bypass AEQ, STAGE1=0, STAGE2=0, Lock Mode = 1
    i2c.write(I2C_ADDRESS_DS90UB954, REG_ADAPTIVE_EQ_BYPASS, 0x01)	#1: Disable adaptive EQ
    time.sleep(0.1)
    # set Parity Error Threshold Hi Register
    i2c.write(I2C_ADDRESS_DS90UB954, REG_PAR_ERR_THOLD_HI, 0x00)
    time.sleep(0.1)
    # set Parity Error Threshold Lo Register
    i2c.write(I2C_ADDRESS_DS90UB954, REG_PAR_ERR_THOLD_LO, 0x01)
    time.sleep(0.1)
    # Enable Encoder CRC error capability
    i2ctemp = SMBus(which_bus, force=True)
    enc_crc = i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_FPD3_CAP)
    i2c.write(I2C_ADDRESS_DS90UB954, REG_FPD3_CAP, (enc_crc | 0x10))
    i2ctemp.close()
    #1: Enable CRC error flag from FPD-Link III encoder

    # Enable Encoder CRC
    i2ctemp = SMBus(which_bus, force=True)
    enc_crc = i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_FPD3_ENC_CTL)
    i2c.write(I2C_ADDRESS_DS90UB954, REG_FPD3_ENC_CTL, (enc_crc & 0x7F))
    i2ctemp.close()


    lock_result = [] #initialize lock_result


    status_color = MarginRequest("Do you want a colored map? (y/n)")
    status_color.yes_no()
    print()

    # delay before lock is checked,
    # use minimum of 0.5 when doing digital reset
    #standard 0.9 seconds
    dwell_time = MarginInput("the", "dwell time", 0.9)
    dwell_time.float_input(500, 60000)


    lock_run = MarginInput("number of", "lock runs", 10)
    lock_run.int_input()

    #standard 0.1 seconds
    lock_time = MarginInput("a", "lock time", 0.1)
    lock_time.float_input(100, 1500)

    print("current dwell time: ", dwell_time.output(), "s")
    print("current lock runs:   ", lock_run.output(), " times")
    print("current lock time:  ", lock_time.output(), "s")
    print()

    strobe_position = MarginPosition("Strobe Position")
    strobe_position.yes_no()
    if strobe_position.output() == 1:
        strobe_position.begin_end(0, 14)
    print("current Strobe Position Begin: ", strobe_position.begin())
    print("current Strobe Position End:   ", strobe_position.end(), "\n")

    eq_position = MarginPosition("EQ Position")
    eq_position.yes_no()
    if eq_position.output() == 1:
        eq_position.begin_end(0, 14)
    print("current EQ Position Begin: ", eq_position.begin())
    print("current EQ Position End:   ", eq_position.end(), "\n")

    clock_base_delay = MarginRequest("Do you want a clock base delay? (y/n)")
    clock_base_delay.yes_no()
    print()

    data_base_delay = MarginRequest("Do you want a data base delay? (y/n)")
    data_base_delay.yes_no()
    print()

    #print("strobe: ", strobe_position.end() + 1 - strobe_position.begin())
    #print ("eq:     ", eq_position.end() + 1 - eq_position.begin())
    take_seconds = ((strobe_position.end() + 1 - strobe_position.begin()) *
                    (eq_position.end() + 1 - eq_position.begin()) *
                    (lock_run.output() * 3 * lock_time.output() +
                     dwell_time.output()))
    print("\nREMAINING TIME: The test will take about",
          round(int(take_seconds) / 60), "minute(s)\n\n")
    #print("\nREMAINING TIME: The test will take about",
    #   round(float(take_seconds) / 60, 2), "minute(s)\n\n")



    if ((strobe_position.begin() < 8) and (strobe_position.end() < 8)):
        #cdly goes high to low, so begin with high
        cdly_high = 7 - strobe_position.begin()
        cdly_low = 8 - strobe_position.end() - 1
        ddly_low = 1
        ddly_high = 0
    if ((strobe_position.begin() >= 8) and (strobe_position.end() >= 8)):
        ddly_low = strobe_position.begin() - 7
        ddly_high = strobe_position.end() - 8 + 1
        cdly_high = 0
        cdly_low = 1
    if strobe_position.begin() < 8 <= strobe_position.end():
        cdly_high = 7 - strobe_position.begin()
        cdly_low = 1
        ddly_low = 0
        ddly_high = strobe_position.end() - 7
    if clock_base_delay.output():
        cdly_low += 8
        cdly_high += 8
    if data_base_delay.output():
        ddly_low += 8
        ddly_high += 8
    if ((eq_position.begin() < 8) and (eq_position.end() < 8)):
        eq1_low = eq_position.begin()
        eq1_high = eq_position.end()
        eq2_low = 0
        eq2_high = -1
    if ((eq_position.begin() >= 8) and (eq_position.end() >= 8)):
        eq2_low = eq_position.begin() - 7
        eq2_high = eq_position.end() - 7
        eq1_low = 0
        eq1_high = -1
    if eq_position.begin() < 8 <= eq_position.end():
        eq1_low = eq_position.begin()
        eq1_high = 7
        eq2_low = 1
        eq2_high = eq_position.end() - 7



    print("\n################## MARGIN ANALYSIS STATUS #################")
    print(" EQ\\SP  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 ")
    if eq_position.begin() != 0:
        for i in range(0, eq_position.begin()):
            if i < 10:
                print("\n   ", i, end="  ")
                out_string = ("\n " + str(i) + ",0.0,0.0,0.0,0.0,0.0,0.0,0.0,"+
                              "0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,")
            else:
                print("\n  ", i, end="  ")
                out_string = ("\n" + str(i) + ",0.0,0.0,0.0,0.0,0.0,0.0,0.0,"+
                              "0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,")
            table.write(out_string)

    eq_sel2 = 0
    #eq_sel1 is needed from 0 to 7
    #8 Durchlaeufe:  0xD4 = 1, 33, 65, 97, 129, 161, 193, 225
    for eq_sel1 in range(eq1_low, eq1_high+1, 1):
        a_array = []
        i2c.write(I2C_ADDRESS_DS90UB954, REG_ADAPTIVE_EQ_BYPASS, ((eq_sel1<<5)+(eq_sel2<<1)+0x01))
            #eq_sel1 Bitweise um 5 Stellen nach links verschieben
            #z.B 2=(10) --> (100 0000) = 64

        if data_base_delay.output():
            ddly_ctrl = 8
        else:
            ddly_ctrl = 0
        table.write("\n")
        print("\n   ", eq_sel1, end="  ")
        out_string = " " + str(eq_sel1) + ","
        table.write(out_string)

        if strobe_position.begin() != 0:
            for i in range(0, strobe_position.begin()):
                print("  ", end=" ")
                out_string = str(0.0) + ","
                table.write(out_string)

        #ddly_ctrl = 8 #(disable 6 extra delay)
        #7 Durchlaeufe:  0xB2 = 143, 142, 141, 140, 139, 138, 137    8x7=56
        for cdly_ctrl in range(cdly_high, cdly_low-1, -1):
            i2c.write(I2C_ADDRESS_DS90UB954, REG_IND_ACC_DATA, ((ddly_ctrl<<4) + cdly_ctrl))
            # reset digital block except registers
            i2c.write(I2C_ADDRESS_DS90UB954, REG_RESET, 0x01)
            time.sleep(dwell_time.output())
            i2ctemp = SMBus(which_bus, force=True)
            port_status1 = i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_RX_PORT_STS1)
            # print(f"Reading status from port {port_status1:08b}") # debug if we read the correct port
            port_status2 = i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_RX_PORT_STS2)
            lock_sum = 0
            for i in range(0, lock_run.output(), 1):
                port_status1 = i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_RX_PORT_STS1)
                time.sleep(lock_time.output())
                port_status2 = i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_RX_PORT_STS2)
                time.sleep(lock_time.output())
                if (((port_status1 & 0x3C) == 0) and
                        ((port_status2 & 0x20) == 0)):
                    lock_sum += int(port_status1 & 0x01)
                else:
                    i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_RX_PAR_ERR_LO)
                    #clear parity error
                time.sleep(lock_time.output())
            i2ctemp.close()
            lock_avg = round(float(lock_sum) / lock_run.output(), 2)
            lock_str = "%0.1f" %lock_avg
            eq_wert = float(lock_sum/lock_run.output())
            a_array.append(float(eq_wert))
            #print((ddly_ctrl<<4) + cdly_ctrl, ddly_ctrl, cdly_ctrl, end=" ")
            status_color.color_output(status_color.output(), eq_wert)
            out_string = lock_str + ","
            table.write(out_string)
        #print("2.cbd_out:", clock_base_delay.output(), end=" ")
        if clock_base_delay.output():
            cdly_ctrl = 8
        else:
            cdly_ctrl = 0


        #cdly_ctrl = 8 #(disable 6 extra delay)
        #8 Durchlaeufe:  0xB2 = 136,152,168,184,200,216,232,2488x8=64
        for ddly_ctrl in range(ddly_low, ddly_high+1, 1):
            # write reg_8
            i2c.write(I2C_ADDRESS_DS90UB954, REG_IND_ACC_DATA, ((ddly_ctrl<<4) + cdly_ctrl))
            # reset digital block except registers
            i2c.write(I2C_ADDRESS_DS90UB954, REG_RESET, 0x01)
            time.sleep(dwell_time.output())
            i2ctemp = SMBus(which_bus, force=True)
            port_status1 = i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_RX_PORT_STS1)
            port_status2 = i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_RX_PORT_STS2)
            lock_sum = 0
            for i in range(0, lock_run.output(), 1):
                port_status1 = i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_RX_PORT_STS1)
                time.sleep(lock_time.output())
                port_status2 = i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_RX_PORT_STS2)
                time.sleep(lock_time.output())
                if (((port_status1 & 0x3C) == 0) and
                        ((port_status2 & 0x20) == 0)):
                    lock_sum += int(port_status1 & 0x01)
                else:
                    i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_RX_PAR_ERR_LO)
                    #clear parity error
                time.sleep(lock_time.output())
            i2ctemp.close()
            lock_avg = round(float(lock_sum) / lock_run.output(), 2)
            lock_str = "%0.1f" %lock_avg
            eq_wert = float(lock_sum/lock_run.output())
            a_array.append(float(eq_wert))
            status_color.color_output(status_color.output(), eq_wert)
            out_string = lock_str + ","
            table.write(out_string)

        if strobe_position.end() != 14:
            for i in range(strobe_position.end(), 14):
                out_string = "0.0,"
                table.write(out_string)
        lock_result.append(a_array)

    ###########################################################################

    eq_sel1 = 7
    #eq_sel2 is needed only from 1 to 7
    #7 Durchlaeufe:  0xD4 = 227, 229, 231, 233, 235, 237, 239
    for eq_sel2 in range(eq2_low, eq2_high+1, 1):
        a_array = []
        i2c.write(I2C_ADDRESS_DS90UB954, REG_ADAPTIVE_EQ_BYPASS, ((eq_sel1<<5)+(eq_sel2<<1)+0x01))
        if data_base_delay.output():
            ddly_ctrl = 8
        else:
            ddly_ctrl = 0
        table.write("\n")
        if (eq_sel1 + eq_sel2) >= 10:
            print("\n  ", eq_sel1 + eq_sel2, end="  ")  #7x eq_sel2
            out_string = str(eq_sel1 + eq_sel2) + ","
        else:
            print("\n   ", eq_sel1 + eq_sel2, end="  ")
            out_string = " " + str(eq_sel1 + eq_sel2) + ","
        table.write(out_string)
        if strobe_position.begin() != 0:
            for i in range(0, strobe_position.begin()):
                print("  ", end=" ")
                out_string = str(0.0) + ","
                table.write(out_string)
        #ddly_ctrl = 8 #(disable 6 extra delay)
        #7 Durchlaeufe:  0xB2 = 143, 142, 141, 140, 139, 138, 137    7x7=49
        for cdly_ctrl in range(cdly_high, cdly_low-1, -1):
            i2c.write(I2C_ADDRESS_DS90UB954, REG_IND_ACC_DATA, ((ddly_ctrl<<4) + cdly_ctrl))
            # reset digital block except registers
            i2c.write(I2C_ADDRESS_DS90UB954, REG_RESET, 0x01)
            time.sleep(dwell_time.output())
            i2ctemp = SMBus(which_bus, force=True)
            port_status1 = i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_RX_PORT_STS1)
            port_status2 = i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_RX_PORT_STS2)
            lock_sum = 0
            for i in range(0, lock_run.output(), 1):
                port_status1 = i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_RX_PORT_STS1)
                time.sleep(lock_time.output())
                port_status2 = i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_RX_PORT_STS2)
                time.sleep(lock_time.output())
                if (((port_status1 & 0x3C) == 0) and
                        ((port_status2 & 0x20) == 0)):
                    lock_sum += int(port_status1 & 0x01)
                else:
                    i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_RX_PAR_ERR_LO)
                    #clear parity error
                time.sleep(lock_time.output())
            i2ctemp.close()
            lock_avg = round(float(lock_sum) / lock_run.output(), 2)
            lock_str = "%0.1f" %lock_avg
            eq_wert = float(lock_sum/lock_run.output())
            a_array.append(float(eq_wert))
            status_color.color_output(status_color.output(), eq_wert)
            out_string = lock_str + ","
            table.write(out_string)

        if clock_base_delay.output():
            cdly_ctrl = 8
        else:
            cdly_ctrl = 0


        #cdly_ctrl = 8 #(disable 6 extra delay)
        #8 Durchlaeufe:  0xB2 = 136,152,168,184,200,216,232,248      7x8=64
        for ddly_ctrl in range(ddly_low, ddly_high+1, 1):
            i2c.write(I2C_ADDRESS_DS90UB954, REG_IND_ACC_DATA, ((ddly_ctrl<<4) + cdly_ctrl))
            # reset digital block except registers
            i2c.write(I2C_ADDRESS_DS90UB954, REG_RESET, 0x01)
            time.sleep(dwell_time.output())
            i2ctemp = SMBus(which_bus, force=True)
            port_status1 = i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_RX_PORT_STS1)
            port_status2 = i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_RX_PORT_STS2)
            lock_sum = 0
            for i in range(0, lock_run.output(), 1):
                port_status1 = i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_RX_PORT_STS1)
                time.sleep(lock_time.output())
                port_status2 = i2ctemp.read_byte_data(I2C_ADDRESS_DS90UB954, REG_RX_PORT_STS2)
                time.sleep(lock_time.output())
                if (((port_status1 & 0x3C) == 0) and
                        ((port_status2 & 0x20) == 0)):
                    lock_sum += int(port_status1 & 0x01)
                else:
                    i2c.read(I2C_ADDRESS_DS90UB954, REG_RX_PAR_ERR_LO)
                    #clear parity error
                time.sleep(lock_time.output())
            i2ctemp.close()
            lock_avg = round(float(lock_sum) / lock_run.output(), 2)
            lock_str = "%0.1f" %lock_avg
            eq_wert = float(lock_sum/lock_run.output())
            a_array.append(float(eq_wert))
            status_color.color_output(status_color.output(), eq_wert)
            out_string = lock_str + ","
            table.write(out_string)
        if strobe_position.end() != 14:
            for i in range(strobe_position.end(), 14):
                out_string = "0.0,"
                table.write(out_string)
        lock_result.append(a_array)

    if eq_position.end() != 14:
        for i in range(eq_position.end(), 14):
            if i < 9:
                print("\n   ", i+1, end="  ")
                out_string = ("\n " + str(i+1) + ",0.0,0.0,0.0,0.0,0.0," +
                              "0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,")
            else:
                print("\n  ", i+1, end="  ")
                out_string = ("\n" + str(i+1) + ",0.0,0.0,0.0,0.0,0.0," +
                              "0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,")
            table.write(out_string)

    print("\n\nLock result:")


    # For printing the lock_result
    c_eq = 0
    r_eq = 0
    eq_0 = 0

    for i in range(eq_position.end()+1 - eq_position.begin()):
        z_0 = 0
        sp_0 = 0
        for j in range(strobe_position.end()+1 - strobe_position.begin()):
            #print(lock_result[i][j], end = " ")
            if lock_result[i][j] == 1.0:
                #print(lock_result[i][j], end = " ")
                print("1.0", end=" ")
                z_0 = z_0 + 1
                if z_0 == 4:
                    eq_0 = eq_0 + 1
            elif (lock_result[i][j] >= 0 and lock_result[i][j] < 1):
                if lock_result[i][j] > 0.9:
                    print(round(((lock_result[i][j])-0.05), 1), end=" ")
                    #round max 0.9
                elif lock_result[i][j] > 0 and lock_result[i][j] < 0.05:
                    print(round(((lock_result[i][j])+0.05), 1), end=" ")
                    #round min 0.1
                else:
                    print(round(lock_result[i][j], 1), end=" ")
                z_0 = 0
            else:
                print("Incorrect input!")
                z_0 = 0

            if (lock_result[i][j] == 1 and
                    lock_result[i][j] == lock_result[i-1][j]):
                sp_0 = sp_0 + 1
                if sp_0 >= 4:
                    c_eq = c_eq + 1
            else:
                sp_0 = 0
        if eq_0 > 0:
            r_eq = r_eq + 1
            eq_0 = 0
            z_0 = 0

        print()
    print()

    if 3 <= r_eq < 10:
        print("EQ-Result is at least 3  --> here: ", r_eq)
        #Gesamt-EQ ist mindestens 3  --> hier:
        out_string = "\nsufficiant EQ lines:,true,\n"

    elif r_eq >= 10:
        print("EQ-Result is at least 3  --> here:", r_eq)
        #Gesamt-EQ nicht ausreichend
        out_string = "\nsufficiant EQ lines:,true,\n"
    else:
        print("EQ-Result is NOT sufficiant!\nFewer than three EQ Levels\n")
        out_string = "\nsufficiant EQ lines:,false,\n"
    table.write(out_string)

    if 1 <= c_eq < 10:
        print("4x2 rectangle available  --> here: ", c_eq)
        #4x2 Rechteck vorhanden      --> hier:
        out_string = "rectangle available:,true,\n"
    elif c_eq >= 10:
        print("4x2 rectangle available  --> here:", c_eq)
        out_string = "rectangle available:,true,\n"
    else:
        print("NO Contiguous Rectangle!")           #Kein Rechteck voranden
        out_string = "rectangle available:,false,\n"
    table.write(out_string)

    print("\n###########################################################")
    if status_color.output() == 1:
        if (r_eq >= 3 and c_eq >= 1):
            print("##########", Bcolors.OK +
                  "RECOMMENDEND: Coax-cable is suitable!" +
                  Bcolors.RESET, "##########")
            #print("#######Coax-Leitung ist geeignet!#######")
            out_string = "Coax-cable suitable:,TRUE,\n"
        else:
            print("######", Bcolors.FAIL +
                  "NOT RECOMMENDEND: Coax-cable is NOT suitable!" +
                  Bcolors.RESET, "######")
            #print("##### Coax-Leitung ist UNGEEIGNET! #####")
            out_string = "Coax-cable suitable:,FALSE,\n"
    if status_color.output() == 0:
        if (r_eq >= 3 and c_eq >= 1):
            print("########## RECOMMENDEND: " +
                  "Coax-cable is suitable! ##########")
            out_string = "Coax-cable suitable:,TRUE,\n"
        else:
            print("###### NOT RECOMMENDEND: " +
                  "Coax-cable is NOT suitable! ######")
            out_string = "Coax-cable suitable:,FALSE,\n"
    table.write(out_string)
    print("###########################################################")




    # write reg_8 default value
    i2c.write(I2C_ADDRESS_DS90UB954, REG_IND_ACC_DATA, 0x0)
    time.sleep(0.1)

    #do a final digital reset including registers
    i2c.write(I2C_ADDRESS_DS90UB954, REG_RESET, 0x02)
    time.sleep(0.1)

    #readback RX_PORT_STS1 to clear Lock status changed on RX Port 0
    i2c.read(I2C_ADDRESS_DS90UB954, REG_RX_PORT_STS1)
    time.sleep(0.1)
    print("\n")


    table.write("\nParameter\n")
    if digital_reset.output() == 1:
        out_string = "Digital Reset:,yes,\n"
    else:
        out_string = "Digital Reset:,no,\n"
    table.write(out_string)
    table.write("dwell time:," + str(dwell_time.output()) + ",s,\n")
    table.write("lock runs:," + str(lock_run.output()) + ",times,\n")
    table.write("lock time:," + str(lock_time.output()) + ",s,\n")
    table.write("Strobe Position Begin:," +
                str(strobe_position.begin_variable) + ",\n")
    table.write("Strobe Position End:," +
                str(strobe_position.end_variable) + ",\n")
    table.write("EQ Position Begin:," +
                str(eq_position.begin_variable) + ",\n")
    table.write("EQ Position End:," + str(eq_position.end_variable) + ",\n")
    if clock_base_delay.output() == 1:
        out_string = "Clock Base Delay:,yes,\n"
    else:
        out_string = "Clock Base Delay:,no,\n"
    table.write(out_string)
    if data_base_delay.output() == 1:
        out_string = "Data Base Delay:,yes,\n"
    else:
        out_string = "Data Base Delay:,no,\n"
    table.write(out_string)
    table.write("Remaining Time:," + str(take_seconds / 60) + ",minute(s),\n")

    table.close()


if __name__ == "__main__":
    main()
