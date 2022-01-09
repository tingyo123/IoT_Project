#! /usr/bin/python2

import time
import sys

EMULATE_HX711=False

referenceUnit = 440

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711
    
GPIO.setwarnings(False)

def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()
    
hx_50 = HX711(23, 24)
hx_10 = HX711(25, 16)
hx_5 = HX711(5, 6)
hx_1 = HX711(17, 27)

# I've found out that, for some reason, the order of the bytes is not always the same between versions of python, numpy and the hx711 itself.
# Still need to figure out why does it change.
# If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
# There is some code below to debug and log the order of the bits and the bytes.
# The first parameter is the order in which the bytes are used to build the "long" value.
# The second paramter is the order of the bits inside each byte.
# According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.

hx_50.set_reading_format("MSB", "MSB")
hx_10.set_reading_format("MSB", "MSB")
hx_5.set_reading_format("MSB", "MSB")
hx_1.set_reading_format("MSB", "MSB")

# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
#hx.set_reference_unit(113)

hx_50.set_reference_unit(referenceUnit)
hx_10.set_reference_unit(referenceUnit)
hx_5.set_reference_unit(referenceUnit)
hx_1.set_reference_unit(referenceUnit)

hx_50.reset()
hx_10.reset()
hx_5.reset()
hx_1.reset()

hx_50.tare()
hx_10.tare()
hx_5.tare()
hx_1.tare()

print("Tare done! Add weight now...")

# to use both channels, you'll need to tare them both
#hx.tare_A()
#hx.tare_B()

while True:
    try:
        # These three lines are usefull to debug wether to use MSB or LSB in the reading formats
        # for the first parameter of "hx.set_reading_format("LSB", "MSB")".
        # Comment the two lines "val = hx.get_weight(5)" and "print val" and uncomment these three lines to see what it prints.
        
        # np_arr8_string = hx.get_np_arr8_string()
        # binary_string = hx.get_binary_string()
        # print binary_string + " " + np_arr8_string
        
        # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
        
        val_50 = hx_10.get_weight(5)
        val_10 = hx_10.get_weight(5)
        val_5 = hx_10.get_weight(5)
        val_1 = hx_1.get_weight(5)
        
        numOf_50 = round((abs(val_50 - 0.0) / 10.0))
        numOf_10 = round((abs(val_10 - 0.0) / 7.8))
        numOf_5 = round((abs(val_5 - 0.0) / 4.55))
        numOf_1 = round((abs(val_1 - 0.0) / 4.0))
        
        subtotal_50 = numOf_50*50
        subtotal_10 = numOf_10*10
        subtotal_5 = numOf_5*5
        subtotal_1 = numOf_1*1
        total = subtotal_50 + subtotal_10 + subtotal_5 + subtotal_1
        
        print("50NTD:%d" %numOf_50)
        print("10NTD:%d" %numOf_10)
        print("5NTD:%d" %numOf_5)
        print("1NTD:%d" %numOf_1)
        print("total:", total)

        # To get weight from both channels (if you have load cells hooked up 
        # to both channel A and B), do something like this
        #val_A = hx.get_weight_A(5)
        #val_B = hx.get_weight_B(5)
        #lprint "A: %s  B: %s" % ( val_A, val_B )
        
        hx_50.power_down()
        hx_10.power_down()
        hx_5.power_down()
        hx_1.power_down()
        
        hx_50.power_up()
        hx_10.power_up()
        hx_5.power_up()
        hx_1.power_up()
        time.sleep(0.1)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
        

