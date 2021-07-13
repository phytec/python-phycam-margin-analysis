#!/usr/bin/env python

from smbus import SMBus
import smbus

import time
import os
import sys

import ma_classes



def main():
    """
    Main program function
    """

    # Define registers values from datasheet
    I2CADDRESSD = 0x3D  # Address of DS90UB954  device
    I2CADDRESSS = 0x30  # Address of DS90UB953  device


    #MARGIN ANALYSIS
    print("\n###########################################################")
    print("##################### MARGIN ANALYSIS #####################")
    print("###########################################################")
    print("date:",time.strftime("%d.%m.%Y\ntime: %H:%M:%S\n",time.localtime()))


    #lock result file
    table=open("./ma_lock_result.txt",  "w+")
    table.write("date:," + time.strftime("%d.%m.%Y,\ntime:,%H:%M:%S,\n", 
        time.localtime()))
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
            i2cbus = SMBus(which_bus)  # Create a new I2C bus
            #TEST: the value of Port B has to be 122
            portb = i2cbus.read_byte_data(I2CADDRESSD, 0x00)
            if which_bus >= 0 and portb == 122:
                print("BUS-check: OK")
                break
            else:
                print("Incorrect input, please try again!\n")
        except:
            print("Incorrect input, please try again!\n")
    print()
    i2c = ma_classes.I2C(which_bus)
    #i2c.detect()
    
    
    #do a final digital reset including registers if selected
    digital_reset = ma_classes.MarginRequest("Do you want to do a final " +
        "digital reset including registers before starting the test? (y/n)")
    digital_reset.yes_no()
    if digital_reset.output() == 1:
        i2cbus.write_byte_data(I2CADDRESSD, 0x01, 0x02)
    else:
        print("\rNo final digital reset!")
    print()


    #set RX_PORT_CTL register
    i2cbus.write_byte_data(I2CADDRESSD,0x0C,0x83)
    #Port 0 and Port1 Receiver enabled, Port 0 Receiver Lock
    time.sleep(0.1)
    #set FPD3_PORT_SEL register
    i2cbus.write_byte_data(I2CADDRESSD,0x4c,0x01)
    #Write Enable for RX port 0 registers -> 0x01: writes enabled
    time.sleep(0.1)
    # choose analog register page
    i2cbus.write_byte_data(I2CADDRESSD, 0xB0, 0x04)
    #FPD-Link III RX Port 0 Reserved Registers: Test and Debug registers
    time.sleep(0.1)

    
    # choose reg_8 @ offset 8
    i2cbus.write_byte_data(I2CADDRESSD, 0xB1, 0x08)
    time.sleep(0.1)
    # configure AEQ_CTL register: Disable SFILTER adaption with AEQ
    i2cbus.write_byte_data(I2CADDRESSD, 0x42, 0x70)	
    #AEQ Error Control: [6] FPD-Link III clock errors, 
    #                   [5] Packet encoding errors, [4] Parity errors
    time.sleep(0.1)
    # set AEQ Bypass register: bypass AEQ, STAGE1=0, STAGE2=0, Lock Mode = 1
    i2cbus.write_byte_data(I2CADDRESSD, 0xD4, 0x01)	#1: Disable adaptive EQ
    time.sleep(0.1)
    # set Parity Error Threshold Hi Register 
    i2cbus.write_byte_data(I2CADDRESSD, 0x05, 0x00)
    time.sleep(0.1)
    # set Parity Error Threshold Lo Register 
    i2cbus.write_byte_data(I2CADDRESSD, 0x06, 0x01)
    time.sleep(0.1)
    # Enable Encoder CRC error capability
    enc_crc = i2cbus.read_byte_data(I2CADDRESSD, 0x4A)
    i2cbus.write_byte_data(I2CADDRESSD, 0x4A, (enc_crc | 0x10))	
    #1: Enable CRC error flag from FPD-Link III encoder
    
    # Enable Encoder CRC
    enc_crc = i2cbus.read_byte_data(I2CADDRESSD, 0xBA)
    i2cbus.write_byte_data(I2CADDRESSD, 0xBA, (enc_crc & 0x7F))
 


    for y in range(0,1):
        lock_result = [] #initialize lock_result


        status_color = ma_classes.MarginRequest("Do you want a " + 
            "colored map? (y/n)")
        status_color.yes_no()
        print()
        
        # delay before lock is checked, 
        # use minimum of 0.5 when doing digital reset
        #standard 0.9 seconds
        dwell_time = ma_classes.MarginInput("the", "dwell time", 0.9)
        dwell_time.float_input(500, 60000)


        lock_run = ma_classes.MarginInput("number of", "lock runs", 10)
        lock_run.int_input()

        #standard 0.1 seconds
        lock_time = ma_classes.MarginInput("a", "lock time", 0.1)
        lock_time.float_input(100, 1500)
        
        print("current dwell time: ", dwell_time.output(), "s")
        print("current lock runs:   ", lock_run.output(), " times")
        print("current lock time:  ", lock_time.output(), "s")
        print()

        strobe_position = ma_classes.MarginPosition("Strobe Position", 0, 14)
        strobe_position.begin_end(0, 14)


        eq_position = ma_classes.MarginPosition("EQ Position", 0, 14)
        eq_position.begin_end(0, 14)
        print()

        clock_base_delay = ma_classes.MarginRequest("Do you want a " +
            "clock base delay? (y/n)")
        clock_base_delay.yes_no()
        print()

        data_base_delay = ma_classes.MarginRequest("Do you want a " +
            "data base delay? (y/n)")
        data_base_delay.yes_no()
        print()

        #print("strobe: ", strobe_position.end()+1-strobe_position.begin())
        #print ("eq:     ", eq_position.end()+1-eq_position.begin())
        take_seconds = ((strobe_position.end()+1-strobe_position.begin()) * 
            (eq_position.end()+1-eq_position.begin()) * 
            (lock_run.output() * 3 * lock_time.output() + dwell_time.output()))
        print("\nREMAINING TIME: The test will take about", 
            round(int(take_seconds) / 60), "minute(s)\n\n")
        #print("\nREMAINING TIME: The test will take about", 
        #   round(float(take_seconds) / 60, 2), "minute(s)\n\n")

        
        eq_sel2 = 0
        


        if ((strobe_position.begin() < 8) and (strobe_position.end() < 8)):
            #cdly goes high to low, so begin with high
            cdly_high = 7 - strobe_position.begin()
            cdly_low = 8 - strobe_position.end()
            ddly_low = ddly_high = 0
        if ((strobe_position.begin() >= 8) and (strobe_position.end() >= 8)):
            ddly_low = strobe_position.begin() - 7
            ddly_high = strobe_position.end() - 8
            cdly_low = cdly_high = 0
        if ((strobe_position.begin() < 8) and (strobe_position.end() >= 8)):
            cdly_high = 7 - strobe_position.begin()
            cdly_low = 1
            ddly_low = 0
            ddly_high = strobe_position.end() - 7
        if (clock_base_delay.output()):
            cdly_low += 8
            cdly_high += 8
        if (data_base_delay.output()):
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
        if ((eq_position.begin() < 8) and (eq_position.end() >= 8)):
            eq1_low = eq_position.begin()
            eq1_high = 7
            eq2_low = 1
            eq2_high = eq_position.end() - 7 



        print("\n################## MARGIN ANALYSIS STATUS #################")
        print(" EQ\SP  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 ")
        if eq_position.begin() != 0:
            for i in range (0, eq_position.begin()):
                print("\n   ", i, end="  ")
                out_string = ("\n " + str(i) + ",0.0,0.0,0.0,0.0,0.0,0.0,0.0,"+
                    "0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,")
                table.write(out_string)
        
        #eq_sel1 is needed from 0 to 7
        #8 Durchlaeufe:  0xD4 = 1, 33, 65, 97, 129, 161, 193, 225
        for eq_sel1 in range (eq1_low, eq1_high+1, 1):
            a = []
            i2cbus.write_byte_data(I2CADDRESSD, 0xD4, 
                ((eq_sel1<<5)+(eq_sel2<<1)+0x01))
                #eq_sel1 Bitweise um 5 Stellen nach links verschieben
                #z.B 2=(10) --> (100 0000) = 64
            
            if (data_base_delay.output()):
                ddly_ctrl = 8
            else:
                ddly_ctrl = 0     
            table.write("\n")
            print("\n   ", eq_sel1, end="  ")
            out_string = " " + str(eq_sel1) + ","
            table.write(out_string)
            
            if strobe_position.begin() != 0:
                    for i in range (0, strobe_position.begin()):
                        print("  ", end=" ")
                        out_string = str(0.0) + ","
                        table.write(out_string)
            
            #ddly_ctrl = 8 #(disable 6 extra delay)
            #7 Durchlaeufe:  0xB2 = 143, 142, 141, 140, 139, 138, 137    8x7=56
            for cdly_ctrl in range(cdly_high, cdly_low-1, -1):  
                i2cbus.write_byte_data(I2CADDRESSD, 0xB2, 
                    ((ddly_ctrl<<4) + cdly_ctrl))
                # reset digital block except registers
                i2cbus.write_byte_data(I2CADDRESSD, 0x01, 0x01)
                time.sleep(dwell_time.output())
                port_status1 = i2cbus.read_byte_data(I2CADDRESSD, 0x4D)
                port_status2 = i2cbus.read_byte_data(I2CADDRESSD, 0x4E)		
                lock_status = 0
                lock_sum = 0
                for loop in range(0, lock_run.output(), 1):
                    port_status1 = i2cbus.read_byte_data(I2CADDRESSD, 0x4D)
                    time.sleep(lock_time.output())
                    port_status2 = i2cbus.read_byte_data(I2CADDRESSD, 0x4E)
                    time.sleep(lock_time.output())			
                    if (((port_status1 & 0x3C) == 0) and 
                        ((port_status2 & 0x20) == 0)):
                        lock_sum += int(port_status1 & 0x01)
                    else:
                        i2cbus.read_byte_data(I2CADDRESSD, 0x56)
                        #clear parity error
                    time.sleep(lock_time.output())
                lock_avg = round(float(lock_sum) / lock_run.output(), 2)
                lock_str = "%0.1f" %lock_avg
                eq_wert = float(lock_sum/lock_run.output())
                a.append(float(eq_wert))
                status_color.color_output(status_color.output(), eq_wert)
                out_string = lock_str + ","
                table.write(out_string)

            if (clock_base_delay.output()): 
                cdly_ctrl = 8
            else:
                cdly_ctrl = 0

                

            #cdly_ctrl = 8 #(disable 6 extra delay)
            #8 Durchlaeufe:  0xB2 = 136,152,168,184,200,216,232,2488x8=64
            for ddly_ctrl in range(ddly_low, ddly_high+1, 1):
                # write reg_8
                i2cbus.write_byte_data(I2CADDRESSD, 0xB2, 
                    ((ddly_ctrl<<4) + cdly_ctrl))
                # reset digital block except registers
                i2cbus.write_byte_data(I2CADDRESSD, 0x01, 0x01)
                time.sleep(dwell_time.output())
                port_status1 = i2cbus.read_byte_data(I2CADDRESSD, 0x4D)
                port_status2 = i2cbus.read_byte_data(I2CADDRESSD, 0x4E)			
                lock_status = 0
                lock_sum = 0
                for loop in range(0, lock_run.output(), 1):
                    port_status1 = i2cbus.read_byte_data(I2CADDRESSD, 0x4D)
                    time.sleep(lock_time.output())
                    port_status2 = i2cbus.read_byte_data(I2CADDRESSD, 0x4E)
                    time.sleep(lock_time.output())				
                    if (((port_status1 & 0x3C) == 0) and 
                        ((port_status2 & 0x20) == 0)):
                        lock_sum += int(port_status1 & 0x01)
                    else:
                        i2cbus.read_byte_data(I2CADDRESSD, 0x56)
                        #clear parity error
                    time.sleep(lock_time.output())
                lock_avg = round(float(lock_sum) / lock_run.output(), 2)
                lock_str = "%0.1f" %lock_avg
                eq_wert = float(lock_sum/lock_run.output())
                a.append(float(eq_wert))
                status_color.color_output(status_color.output(), eq_wert)
                out_string = lock_str + ","
                table.write(out_string)
        
            if strobe_position.end() != 14:
                for i in range (strobe_position.end(), 14):
                        out_string = "0.0,"
                        table.write(out_string)
            lock_result.append(a)
            
###############################################################################
    
        eq_sel1 = 7
        #eq_sel2 is needed only from 1 to 7
        #7 Durchlaeufe:  0xD4 = 227, 229, 231, 233, 235, 237, 239
        for eq_sel2 in range(eq2_low, eq2_high+1, 1):  
            a = []
            i2cbus.write_byte_data(I2CADDRESSD, 0xD4, 
                ((eq_sel1<<5)+(eq_sel2<<1)+0x01))
            if (data_base_delay.output()):
                ddly_ctrl = 8
            else:
                ddly_ctrl = 0   
            table.write("\n")                                                           
            if (eq_sel1 + eq_sel2) < 10:
                print("\n   ", eq_sel1 + eq_sel2, end="  ")
                out_string = " " + str(eq_sel1 + eq_sel2) + ","            
            else:
                print("\n  ", eq_sel1 + eq_sel2, end="  ")  #7x eq_sel2
                out_string = str(eq_sel1 + eq_sel2) + ","
            table.write(out_string)
            if strobe_position.begin() != 0:
                    for i in range (0, strobe_position.begin()):
                        print("  ", end=" ")
                        out_string = str(0.0) + ","
                        table.write(out_string)
            #ddly_ctrl = 8 #(disable 6 extra delay)
            #7 Durchlaeufe:  0xB2 = 143, 142, 141, 140, 139, 138, 137    7x7=49
            for cdly_ctrl in range(cdly_high, cdly_low-1, -1):
                i2cbus.write_byte_data(I2CADDRESSD, 0xB2, 
                    ((ddly_ctrl<<4) + cdly_ctrl))
                # reset digital block except registers
                i2cbus.write_byte_data(I2CADDRESSD, 0x01, 0x01)
                time.sleep(dwell_time.output())
                port_status1 = i2cbus.read_byte_data(I2CADDRESSD, 0x4D)
                port_status2 = i2cbus.read_byte_data(I2CADDRESSD, 0x4E)			
                lock_status = 0
                lock_sum = 0
                for loop in range(0, lock_run.output(), 1):
                    port_status1 = i2cbus.read_byte_data(I2CADDRESSD, 0x4D)
                    time.sleep(lock_time.output())
                    port_status2 = i2cbus.read_byte_data(I2CADDRESSD, 0x4E)
                    time.sleep(lock_time.output())				
                    if (((port_status1 & 0x3C) == 0) and 
                        ((port_status2 & 0x20) == 0)):
                        lock_sum += int(port_status1 & 0x01)
                    else:
                        i2cbus.read_byte_data(I2CADDRESSD, 0x56)
                        #clear parity error
                    time.sleep(lock_time.output())
                lock_avg = round(float(lock_sum) / lock_run.output(), 2)
                lock_str = "%0.1f" %lock_avg
                eq_wert = float(lock_sum/lock_run.output())
                a.append(float(eq_wert))
                status_color.color_output(status_color.output(), eq_wert)
                out_string = lock_str + ","
                table.write(out_string)
            
            if (clock_base_delay.output()): 
                cdly_ctrl = 8
            else:
                cdly_ctrl = 0

                                
            #cdly_ctrl = 8 #(disable 6 extra delay)
            #8 Durchlaeufe:  0xB2 = 136,152,168,184,200,216,232,248      7x8=64
            for ddly_ctrl in range(ddly_low, ddly_high+1, 1):   
                i2cbus.write_byte_data(I2CADDRESSD, 0xB2, 
                    ((ddly_ctrl<<4) + cdly_ctrl))
                # reset digital block except registers
                i2cbus.write_byte_data(I2CADDRESSD, 0x01, 0x01)
                time.sleep(dwell_time.output())
                port_status1 = i2cbus.read_byte_data(I2CADDRESSD, 0x4D)
                port_status2 = i2cbus.read_byte_data(I2CADDRESSD, 0x4E)			
                lock_status = 0
                lock_sum = 0
                for loop in range(0, lock_run.output(), 1):
                    port_status1 = i2cbus.read_byte_data(I2CADDRESSD, 0x4D)
                    time.sleep(lock_time.output())
                    port_status2 = i2cbus.read_byte_data(I2CADDRESSD, 0x4E)
                    time.sleep(lock_time.output())				
                    if (((port_status1 & 0x3C) == 0) and 
                        ((port_status2 & 0x20) == 0)):
                        lock_sum += int(port_status1 & 0x01)
                    else:
                        i2cbus.read_byte_data(I2CADDRESSD, 0x56)
                        #clear parity error	
                    time.sleep(lock_time.output())
                lock_avg = round(float(lock_sum) / lock_run.output(), 2)
                lock_str = "%0.1f" %lock_avg
                eq_wert = float(lock_sum/lock_run.output())
                a.append(float(eq_wert))
                status_color.color_output(status_color.output(), eq_wert)
                out_string = lock_str + ","
                table.write(out_string)
            if strobe_position.end() != 14:
                for i in range (strobe_position.end(), 14):
                        out_string = "0.0,"
                        table.write(out_string)
            lock_result.append(a)
        
        if eq_position.end() != 14:
            for i in range (eq_position.end(), 14):
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
        z_eq = 0
        eq = 0
        r_eq = 0
        for i in range(eq_position.end()+1 - eq_position.begin()):
            z = 0
            sp = 0
            for j in range(strobe_position.end()+1 - strobe_position.begin()):
                #print(lock_result[i][j], end = " ")
                if (lock_result[i][j] == 1.0):
                    #print(lock_result[i][j], end = " ")
                    print("1.0", end = " ")
                    z = z + 1
                    if (z == 4):
                        eq = eq +1
                elif (lock_result[i][j] >= 0 and lock_result[i][j] < 1):
                    if lock_result[i][j] > 0.9:
                        print(round(((lock_result[i][j])-0.05), 1), end = " ")
                        #round max 0.9
                    elif lock_result[i][j] > 0 and lock_result[i][j] < 0.05:
                        print(round(((lock_result[i][j])+0.05), 1), end = " ")
                        #round min 0.1
                    else:
                        print(round(lock_result[i][j], 1), end = " ")
                    z = 0
                else:
                    print("Incorrect input!")
                    z = 0
                
                if (lock_result[i][j] == 1 and 
                    lock_result[i][j] == lock_result[i-1][j]):
                    sp = sp + 1
                    if (sp >= 4):
                        z_eq = z_eq + 1
                else:  
                    sp = 0
            if eq > 0:
                r_eq = r_eq + 1
                eq = 0
                z = 0

            print()
        print()
        
        if (r_eq >= 3 and r_eq < 10):
            print("EQ-Result is at least 3  --> here: ", r_eq)
            #Gesamt-EQ ist mindestens 3  --> hier:
            out_string = "\nsufficiant EQ lines:,true,\n"
            
        elif (r_eq >= 10):
            print("EQ-Result is at least 3  --> here:", r_eq)
            #Gesamt-EQ nicht ausreichend
            out_string = "\nsufficiant EQ lines:,true,\n"
        else:
            print("EQ-Result is NOT sufficiant!\nFewer than Three EQ Levels\n")
            out_string = "\nsufficiant EQ lines:,false,\n"
        table.write(out_string)

        if (z_eq >= 1 and z_eq < 10):
            print("4x2 rectangle available  --> here: ", z_eq)
            #4x2 Rechteck vorhanden      --> hier:
            out_string = "rectangle available:,true,\n"
        elif (z_eq >= 10):
            print("4x2 rectangle available  --> here:", z_eq)
            out_string = "rectangle available:,true,\n"
        else:
            print("NO Contiguous Rectangle!")           #Kein Rechteck voranden
            out_string = "rectangle available:,false,\n"
        table.write(out_string)
        
        print("\n###########################################################")
        if status_color.output() == 1:
            if (r_eq >= 3 and z_eq >= 1):
                print("##########", ma_classes.Bcolors.OK + 
                    "RECOMMENDEND: Coax-cable is suitable!" + 
                    ma_classes.Bcolors.RESET, "##########")
                #print("#######Coax-Leitung ist geeignet!#######")
                out_string = "Coax-cable suitable:,TRUE,\n"
            else:
                print("######", ma_classes.Bcolors.FAIL + 
                    "NOT RECOMMENDEND: Coax-cable is NOT suitable!" + 
                    ma_classes.Bcolors.RESET, "######")
                #print("##### Coax-Leitung ist UNGEEIGNET! #####")
                out_string = "Coax-cable suitable:,FALSE,\n"
        if status_color.output() == 0:
            if (r_eq >= 3 and z_eq >= 1):
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
    i2cbus.write_byte_data(I2CADDRESSD, 0xB2, 0x0)
    time.sleep(0.1)

    #do a final digital reset including registers
    i2cbus.write_byte_data(I2CADDRESSD, 0x01, 0x02)
    time.sleep(0.1)

    #readback RX_PORT_STS1 to clear Lock status changed on RX Port 0
    i2cbus.read_byte_data(I2CADDRESSD, 0x4D)
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