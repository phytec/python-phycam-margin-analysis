#!/usr/bin/env python

from smbus import SMBus
import smbus
import sys


class I2C:
    def __init__(self, dev_address):
        self.i2c = smbus.SMBus(dev_address) # i2c bus: J8.3 (GPIO2) as SDA,
                                            # J8.5 (GPIO3) as SCL
    
    def detect(self):
        # inspired by shell command "i2cdetect -y 2"
        print('     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f')
        for addr in range(0, 127, 16):
            lin = '{:02x}:'.format(addr)
            for i in range(0, 16):
                if addr + i < 3:
                    lin += '   '
                else:
                    try:
                        x = self.i2c.write_i2c_block_data(addr + i, 0, [])
                    except OSError:
                        lin += ' --'
                    else:
                        lin += ' {:02x}'.format(addr + i)
            print(lin)
                            
    def read(self, addr, reg, cnt):
        # returns a list of received data
        data = self.i2c.read_i2c_block_data(addr, reg, cnt)
        print('<RD addr {}, reg/ofs {} = {}'.format(hex(addr),
                                                    hex(reg),
                                                    data))
        return data
        
    def write(self, addr, reg, data):
        # no return value
        self.i2c.write_i2c_block_data(addr, reg, data)
        print('>WR addr {}, reg/ofs {}: {}'.format(
                hex(addr),
                hex(reg),
                'set register' if data == [] else data))


class Bcolors:
    OK = '\033[32m' #GREEN
    WARNING = '\033[33m' #YELLOW
    FAIL = '\033[31m' #RED
    RESET = '\033[0m' #RESET COLOR


class MarginRequest():
    def __init__(self, question):
        self.question = question
        self.variable = 0

    def yes_no(self):
        while True:
            print()
            print(self.question)
            ma_input = input()
            if ma_input == "j" or ma_input == "y" or ma_input == "Y":
                self.variable = 1
                break
            elif ma_input == "n" or ma_input == "N" or ma_input == "no":
                self.variable = 0
                break
            else:
                print("Incorrect input, please try again!")
        return self.variable

    def color_output(self, s_c_output, eq_value):
        if s_c_output == 1:
            if (eq_value == 1):
                print(Bcolors.OK + "▇▇" + Bcolors.RESET, end=" ")
                #sys.stdout.write(Bcolors.OK + "▇▇ " + Bcolors.RESET)
            elif (eq_value == 0):
                print(Bcolors.FAIL + "▇▇" + Bcolors.RESET, end=" ")
                #sys.stdout.write(Bcolors.FAIL + "▇▇ " + Bcolors.RESET)
            else:
                print(Bcolors.WARNING + "▇▇" + Bcolors.RESET, end=" ")
                #sys.stdout.write(Bcolors.WARNING + "▇▇ " + Bcolors.RESET)
        if s_c_output == 0:
            if (eq_value == 1):
                #print("##", end=" ")
                print("██", end=" ")
            elif (eq_value == 0):
                #print("  ", end=" ")
                print("--", end=" ")
            else:
                #print("--", end=" ")
                print("▒▒", end=" ") #7x lock status #7x lock status
    
    def output(self):
        return self.variable


class MarginInput:
    def __init__(self, article, what, variable):
        self.article = article
        self.what = what
        self.variable = variable

    def float_input(self, start, end):
        while True:
            print("\nDo you want to set",self.article, self.what, "? (y/n)")
            ma_input = input()
            if ma_input == "j" or ma_input == "y" or ma_input == "Y":
                print()
                while True:
                    print("Enter a value between", start, "and", end, "(ms):")
                    variable = input()
                    try:
                        variable = float(variable)
                        if variable >= start and variable <= end:
                            self.variable = variable / 1000
                            break
                        else:
                            print("\nPlease try again!")
                    except:
                        print("\nPlease try again!")
                break
            elif ma_input == "n" or ma_input == "N" or ma_input == "no":
                print("The", self.what, "value", 
                    self.variable, "is set by default")
                break
            else:
                print("Incorrect input, please try again!")
        print("current", self.what, ": ", self.variable, "second(s)\n")
        return self.variable

    def int_input(self):
        while True:
            print("\nDo you want to set",self.article, self.what, "? (y/n)")
            ma_input = input()
            if ma_input == "j" or ma_input == "y" or ma_input == "Y":
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
                        else:
                            print("\nPlease try again!")
                    except:
                        print("\nPlease try again!")
                break
            elif ma_input == "n" or ma_input == "N" or ma_input == "no":
                print("The", self.what, "value", 
                    self.variable, "is set by default")
                break
            else:
                print("Incorrect input, please try again!")
        print("current", self.what, ": ", self.variable, "\n")
        return self.variable
    
    def output(self):
        return self.variable




class MarginPosition:
    def __init__(self, what, begin_variable, end_variable):
        self.what = what
        self.begin_variable = begin_variable
        self.end_variable = end_variable

    def begin_end(self, start, end):
        while True:
            print("\nDo you want to set",self.what, "? (y/n)")
            ma_input = input()
            if ma_input == "j" or ma_input == "y" or ma_input == "Y":
                print()
                while True:
                    print("Enter integer values from", start, "to", end,":")
                    print(self.what, "Begin:")
                    begin_variable = input()
                    try:
                        begin_variable = int(begin_variable)
                        if begin_variable >= start and begin_variable <= end:
                            self.begin_variable = begin_variable
                            print(self.what, "End:")
                            end_variable = input()
                            try:
                                end_variable = int(end_variable)
                                if (end_variable >= start and 
                                    end_variable <= end and 
                                    begin_variable < end_variable):
                                    self.end_variable = end_variable
                                    break
                                else:
                                    print("\nPlease try again!")
                            except:
                                print("\nPlease try again!")
                        else:
                            print("\nPlease try again!")
                    except:
                        print("\nPlease try again!")
                break
            elif ma_input == "n" or ma_input == "N" or ma_input == "no":
                print("The", self.what, "start value", self.begin_variable, 
                    "and", self.what, "end value", 
                    self.end_variable, "is set by default.")
                break
            else:
                print("Incorrect input, please try again!")
        print("current", self.what, "Begin: ", self.begin_variable)
        print("current", self.what, "End:   ", self.end_variable, "\n")
        return self.begin_variable
        return self.end_variable

    def begin(self):
        return self.begin_variable

    def end(self):
        return self.end_variable



