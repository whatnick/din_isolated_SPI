EESchema Schematic File Version 2
LIBS:power
LIBS:device
LIBS:transistors
LIBS:conn
LIBS:linear
LIBS:regul
LIBS:74xx
LIBS:cmos4000
LIBS:adc-dac
LIBS:memory
LIBS:xilinx
LIBS:microcontrollers
LIBS:dsp
LIBS:microchip
LIBS:analog_switches
LIBS:motorola
LIBS:texas
LIBS:intel
LIBS:audio
LIBS:interface
LIBS:digital-audio
LIBS:philips
LIBS:display
LIBS:cypress
LIBS:siliconi
LIBS:opto
LIBS:atmel
LIBS:contrib
LIBS:valves
LIBS:SI8661AB-B-IS1
LIBS:wemos_mini
LIBS:BME280
LIBS:din_isolated_SPI-cache
EELAYER 26 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L SI8661AB-B-IS1 U1
U 1 1 59E7536C
P 4000 3250
F 0 "U1" H 4000 4120 50  0000 C CNN
F 1 "SI8661AB-B-IS1" H 4000 4029 50  0000 C CNN
F 2 "Housings_SOIC:SOIC-16_3.9x9.9mm_Pitch1.27mm" H 4000 3250 50  0001 L BNN
F 3 "Silicon Labs" H 4000 3250 50  0001 L BNN
F 4 "2.12 USD" H 4000 3250 50  0001 L BNN "Price"
F 5 "Warning" H 4000 3250 50  0001 L BNN "Availability"
F 6 "General Purpose tal Isolator 2500Vrms 6 Channel 1Mbps 35kV/µs CMTI 16-SOIC (0.154 , 3.90mm Width)" H 4000 3250 50  0001 L BNN "Description"
F 7 "SOIC-16 Silicon Labs" H 4000 3250 50  0001 L BNN "Package"
F 8 "SI8661AB-B-IS1" H 4000 3250 50  0001 L BNN "MP"
	1    4000 3250
	1    0    0    -1  
$EndComp
$Comp
L WeMos_mini U4
U 1 1 59E75C06
P 7200 3150
F 0 "U4" H 7200 3787 60  0000 C CNN
F 1 "WeMos_mini" H 7200 3681 60  0000 C CNN
F 2 "wemos_d1_mini:D1_mini_board" H 7750 2450 60  0001 C CNN
F 3 "" H 7750 2450 60  0000 C CNN
	1    7200 3150
	1    0    0    -1  
$EndComp
$Comp
L MCP7940N U2
U 1 1 59EF4677
P 3900 5000
F 0 "U2" H 3900 4514 50  0000 C CNN
F 1 "MCP7940N" H 3900 4423 50  0000 C CNN
F 2 "Housings_SSOP:TSSOP-8_4.4x3mm_Pitch0.65mm" H 3900 5000 50  0001 C CNN
F 3 "" H 3900 5000 50  0001 C CNN
	1    3900 5000
	1    0    0    -1  
$EndComp
$Comp
L BME280 U3
U 1 1 59EF4871
P 5500 5000
F 0 "U3" H 5500 5878 50  0000 C CNN
F 1 "BME280" H 5500 5787 50  0000 C CNN
F 2 "BME280" H 5500 5000 50  0001 L BNN
F 3 "BME280" H 5500 5000 50  0001 L BNN
F 4 "5.03 USD" H 5500 5000 50  0001 L BNN "Price"
F 5 "Good" H 5500 5000 50  0001 L BNN "Availability"
F 6 "Integrated pressure, humidity and temperature sensor; 8-pin 2.5x2.5x0.93mm LGA" H 5500 5000 50  0001 L BNN "Description"
F 7 "Bosch" H 5500 5000 50  0001 L BNN "MF"
F 8 "LGA-8 Bosch" H 5500 5000 50  0001 L BNN "Package"
	1    5500 5000
	1    0    0    -1  
$EndComp
$EndSCHEMATC
