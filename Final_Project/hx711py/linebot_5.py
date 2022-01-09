import time
import sys

EMULATE_HX711=False

referenceUnit = 440

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711
    
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

GPIO.setwarnings(False)

def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()
    
hx_5 = HX711(5, 6)

# I've found out that, for some reason, the order of the bytes is not always the same between versions of python, numpy and the hx711 itself.
# Still need to figure out why does it change.
# If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
# There is some code below to debug and log the order of the bits and the bytes.
# The first parameter is the order in which the bytes are used to build the "long" value.
# The second paramter is the order of the bits inside each byte.
# According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.

hx_5.set_reading_format("MSB", "MSB")

# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
#hx.set_reference_unit(113)

hx_5.set_reference_unit(referenceUnit)

hx_5.reset()

hx_5.tare()

print("Tare done! Add weight now...")

# to use both channels, you'll need to tare them both
#hx.tare_A()
#hx.tare_B()

app = Flask(__name__)
# LINE BOT info
line_bot_api = LineBotApi('QCynFfsDk7My1YN72sVQyvk6ArYkD2TUQW/pUxUQqllnGFNcqjZ8tKC+qMcVa2u4Lg1WmdUVLcS124tweaXtcVWLmK/thFH1NFUZL/Olev6ugLeKG4VUVd0ee8VUUgnrqqCZD+ZBpD6j61TRW2eJEgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('f3b5d7b57ef1f4d1277aecd7f045db3d')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print(body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# Message event
@handler.add(MessageEvent)
def handle_message(event):
    message_type = event.message.type
    user_id = event.source.user_id
    reply_token = event.reply_token
    message = event.message.text
    if message == "execute":
        line_bot_api.reply_message(reply_token, TextSendMessage(text = "okay~"))
        while True:
            try:
                # These three lines are usefull to debug wether to use MSB or LSB in the reading formats
                # for the first parameter of "hx.set_reading_format("LSB", "MSB")".
                # Comment the two lines "val = hx.get_weight(5)" and "print val" and uncomment these three lines to see what it prints.
                
                # np_arr8_string = hx.get_np_arr8_string()
                # binary_string = hx.get_binary_string()
                # print binary_string + " " + np_arr8_string
                
                # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
                val_5 = hx_5.get_weight(5)
                numOf_5 = round((abs(val_5 - 0.0) / 4.55))
                print("5NTD:%d" %numOf_5)
                print("total:", numOf_5*5)

                # To get weight from both channels (if you have load cells hooked up 
                # to both channel A and B), do something like this
                #val_A = hx.get_weight_A(5)
                #val_B = hx.get_weight_B(5)
                #lprint "A: %s  B: %s" % ( val_A, val_B )

                hx_5.power_down()
                
                hx_5.power_up()
                
                time.sleep(0.1)

            except (KeyboardInterrupt, SystemExit):
                cleanAndExit()
                
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)

