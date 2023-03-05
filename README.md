# IoT Project — Piggy Banky
![](https://i.imgur.com/WI3YCCB.jpg)

---
## Introduction
piggy banky是一個神奇的零錢筒，把你的零錢灑進他的肚子裡，他可以告訴你有多少錢喔!
## Components
### Hardware
* Raspberry Pi Model 3B *1
* Personal Computer (Windows OS) *1
* USB Cable for Raspberry Pi *1
* Micro SD Card 32GB+ *1
* HDMI Cable *1
* Female To Female Dupont Jumper Wires Cable *16
* Digital Load Cell Weight Sensor HX711 AD Converter Breakout Module 5KG *4
### Software
* SD Card Formatter
* Raspbian OS
* RealVNC Client
* Visaul Studio Code
* Python 3.7.3
* Linebot
* Flask
### Tools
* Corrugated Paper
* Cutter Knife *1
* Glue Gun *1
* Hot Glue Sticks *5
* Duct Tape
* Screwdriver
* Colored Paper
* White Paperboard
## Circuit Diagram
![](https://i.imgur.com/UeqSZWT.png)
## Schematic Diagram
![](https://i.imgur.com/FS7fggm.png)

## Setup and Installation
### HX711 Module
#### STEP 1 ： HX711模組組裝
![](https://i.imgur.com/2PAksr1.png)
[ImageSource](https://www.taiwaniot.com.tw/product/hx711%e6%a8%a1%e7%b5%845kg%e5%a3%93%e5%8a%9b%e6%84%9f%e6%b8%ac%e5%99%a8arduino%e5%a5%97%e4%bb%b6%e7%b5%84-%e7%a7%a4%e9%87%8d%e6%84%9f%e6%b8%ac%e5%99%a8-arduino%e9%9b%bb%e5%ad%90%e7%a7%a4%e6%a8%a1/)
1. 24位A/D轉換器，接收壓力感測器的電訊號，並轉為數字訊號
2. 塑膠支撐柱，用來插在秤盤挖好的孔上，支撐整個秤重模組
3. 塑膠墊片，栓在壓力感測器與秤盤之間
4. 金屬插頭，長邊頭接上杜邦線，短邊頭插在24位A/D轉換器上（GND、DT、SCK、VCC那排）
5. 壓力感測器，與塑膠墊片和秤盤拴在一起
6. 螺絲釘，拴住秤盤、塑膠墊片與壓力感測器
7. 杜邦線，一邊連接金屬插頭，另一邊連接Raspberry Pi

![](https://i.imgur.com/TaXzUzw.jpg)
> 注意：上下秤盤與壓力感測器間必須用塑膠墊片間隔，且秤盤必須栓在壓力感測器的兩側，這樣才能讓壓力感測器產生旋轉的力矩並反應出微小的變形，進而測得物體的重量
#### STEP 2：24位A/D轉換器線路連接
![](https://i.imgur.com/0XfTFeK.png)
[ImageSource](https://circuitjournal.com/four-wire-load-cell-with-HX711)
* 24位A/D轉換器與壓力感測器

    * Red -> E+
    * Black -> E-
    * White -> A-
    * Green -> A+

![](https://i.imgur.com/kXHhwHm.png)

[ImageSource](https://tutorials-raspberrypi.com/digital-raspberry-pi-scale-weight-sensor-hx711/)
* 24位A/D轉換器與Raspberry Pi

    * VCC -> Raspberry Pi Pin 2 (5V)
    * GND -> Raspberry Pi Pin 6 (GND)
    * DT -> Raspberry Pi Pin 29 (GPIO 5)
    * SCK -> Raspberry Pi Pin 31 (GPIO 6)

> 注意：VCC可接在Raspberry Pi上3.3V的腳位，DT與SCK也可接在其他GPIO的腳位（避免接在有特殊功能的GPIO腳位，如GPIO 2、GPIO 3，會造成執行時終端機卡住）

#### STEP 3：找一個合適的HX711 Python Library
![](https://i.imgur.com/R6R6rk7.png)

[ImageSource](https://github.com/tatobari/hx711py)
* 在Raspberry Pi的終端機下git clone指令
```
git clone https://github.com/tatobari/hx711py
```
#### 範例介紹(example.py檔)
```
#! /usr/bin/python2

import time
import sys

EMULATE_HX711=False

referenceUnit = 1

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()

hx = HX711(5, 6)

# I've found out that, for some reason, the order of the bytes is not always the same between versions of python, numpy and the hx711 itself.
# Still need to figure out why does it change.
# If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
# There is some code below to debug and log the order of the bits and the bytes.
# The first parameter is the order in which the bytes are used to build the "long" value.
# The second paramter is the order of the bits inside each byte.
# According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.
hx.set_reading_format("MSB", "MSB")

# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
#hx.set_reference_unit(113)
hx.set_reference_unit(referenceUnit)

hx.reset()

hx.tare()

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
        val = hx.get_weight(5)
        print(val)

        # To get weight from both channels (if you have load cells hooked up 
        # to both channel A and B), do something like this
        #val_A = hx.get_weight_A(5)
        #val_B = hx.get_weight_B(5)
        #print "A: %s  B: %s" % ( val_A, val_B )

        hx.power_down()
        hx.power_up()
        time.sleep(0.1)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
```
* 第8行：參考單位，之後在校準的時候需要進行調整

![](https://i.imgur.com/ZRrdSCJ.png)

* 第25行：宣告一個HX711的物件，括號裡第一個參數是DT的腳位，第二個是SCK的腳位

![](https://i.imgur.com/JRKvqek.png)

* 54~76行：執行無限迴圈，以`val`變數不停取得秤得的重量並列印出來

![](https://i.imgur.com/KT0O02I.png)

* 78、79行：此無限迴圈的終止條件，當收到exception時，迴圈會break掉

![](https://i.imgur.com/xj8dnc6.png)

#### STEP 4：進行校準
* clone完之後變更到hx711py資料夾目錄
```
cd hx711py
```
* 執行example.py檔
```
sudo python3 example.py
```
![](https://i.imgur.com/Cbr0Wc9.png)

可以發現數字差不多在-1300至-1500間徘徊，在這裡大概抓-1400
* 然後放上一個已知重量的物品到秤盤上，這裡用新台幣50元當參照物(10g)

![](https://i.imgur.com/5AHu50A.png)

可以看到數字差不多落在3000左右
* 接下來找到hx711py資料夾，開啟example.py檔

![](https://i.imgur.com/6f1Hitq.png)

* 調整`referenceUnit`至`440`（[3000 - (-1400)] / 10g）

![](https://i.imgur.com/dgxUI8k.png)
* Ctrl+S後，再執行一次example.py檔

![](https://i.imgur.com/41oSymS.png)

可以看到秤盤上沒東西時，重量差不多為0g，放上新台幣50元後，重量變為10g左右。到這個階段HX711模組的設置就完成了，接下來可以依自身需求寫程式應用啦!
> 注意：一、若執行時終端機卡住，可能是py檔裡DT或SCK的腳位設定錯誤。二、若執行後，終端機print出的數字亂跳，或是一直為0.0，很可能是線路接觸不良導致。三、此HX711模組校準後的精度在1g內，有些許誤差皆屬正常。

### 應用—精準測得新台幣硬幣的個數與回報金額(以1元為例)
```
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

hx_1 = HX711(17, 27)

hx_1.set_reading_format("MSB", "MSB")

hx_1.set_reference_unit(referenceUnit)

hx_1.reset()

hx_1.tare()

print("Tare done! Add weight now...")

while True:
    try:       
        val_1 = hx_1.get_weight(5)
        numOf_1 = round((abs(val_1 - 0.0) / 4.0))
        print("1NTD:%d" %numOf_1)
        print("total:", numOf_1*1)
        hx_1.power_down()
        hx_1.power_up()
        time.sleep(0.1)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
```
#### [VIDEO](https://youtu.be/DPkNIDD49mc)
## LINE BOT
### LINE Messaging API
API(Application Programming Interface)規範了多個程式之間互動的方式，你只需要透過其規範的使用方式，他就會依照設定的功能回覆，不需要了解他是怎麼實作的就可以運用

LINE Messaging API也是一樣，我們只需要將我們希望回覆的訊息格式以及內容以特定的JSON格式回覆給API，它就會將這則訊息傳給用戶。Messenging API 讓指定的 JSON格式檔案 可以在我們的 BOT Server 及 LINE Platform 之間以HTTPS的方式傳遞

![](https://i.imgur.com/HNSF1YQ.png)
### LINE BOT Setup
#### STEP 1 ： 前往[LINE Developers](https://developers.line.biz/en/)創建與登入LINE帳號
![](https://i.imgur.com/0ydvDuN.jpg)
右上角點擊Log in
#### STEP 2 ： 新增Providers
在登入LINE Developers之後會看到類似這樣的介面
![](https://i.imgur.com/HvyWuao.png)
接著在Providers的部分點擊Create，輸入Providers name，可以隨意取自己想要的名字

![](https://i.imgur.com/Tih0u1K.png)

輸入完畢後按下Create
#### STEP 3 ： 新增Messaging API channel 
點擊第二個「Create a Messaging API channel」
![](https://i.imgur.com/jZTxBhc.png)
#### STEP 4 ： 修改基本資料
* Channel name
![](https://i.imgur.com/hVQuYSJ.png)
* Channel description
![](https://i.imgur.com/mhXzHZT.png)
* Category
![](https://i.imgur.com/NOCgzkh.png)
* Subcategory
![](https://i.imgur.com/oZvxJKR.png)
* Email address
![](https://i.imgur.com/CcPzE4R.png)
#### STEP 5 ： 勾選同意政策並點擊Create
![](https://i.imgur.com/nA53EXq.png)
### 產生Access token
#### STEP 1 ： 回到Messaging API
![](https://i.imgur.com/PBx2A9x.png)
#### STEP 2 ： 滑到最下面找到 Channel access token 並點擊 issue
![](https://i.imgur.com/VgxdCDi.png)
### 啟用webhook
#### STEP 1 ： 前往[Line Manager](https://manager.line.biz/)選擇剛剛新增的BOT
![](https://i.imgur.com/mMMhm6f.png)
#### STEP 2 ： 按右上角「設定」
![](https://i.imgur.com/XtV3fHm.png)
#### STEP 3 ： 選擇左側的回應設定

![](https://i.imgur.com/R2sIXRO.png)

將進階設定中的Webhook勾選啟用並將自動回覆訊息改為停用
![](https://i.imgur.com/SsWgYQj.png)
### 下載Python套件
LINE官方在Python方面有提供line-bot-sdk套件，我們還需要flask套件

#### STEP 1 ： win+R開啟cmd
#### STEP 2 ： 輸入下方指令
`pip3 install line-bot-sdk flask`
### 下載Visual Studio Code
#### STEP 1 ： 前往[VScode](https://code.visualstudio.com/)下載windows版本
![](https://i.imgur.com/kXo0gjE.png)
#### STEP 2 ： 下載Python套件
1. 下載完VScode後開啟
2. 點擊左側四個正方形的Extentions
3. 搜尋Python並下載

![](https://i.imgur.com/jbBj5OY.png)
### 下載ngrok 
#### STEP 1 ： 前往[ngrok](https://ngrok.com/download)官網下載windows版本
![](https://i.imgur.com/f7zH69f.png)
這樣一來我們的設定就完成拉
## LINE BOT Implementation
### Coding
#### STEP 1 ： 在D槽建立一個資料夾

![](https://i.imgur.com/HQWrHRp.png)

名稱可以隨意取，在這裡我們取作linebotTest
#### STEP 2 ： 複製ngrok執行檔（ngrok.exe）到與資料夾同一層的路徑中
![](https://i.imgur.com/QdLGkcH.png)

#### STEP 3 ： 回到VScode
![](https://i.imgur.com/yJRBODu.png)
#### STEP 4 ： 開啟資料夾
1. 點擊左上角的File
2. 選擇Open Folder
3. 點選剛剛建立的linebotTest資料夾

![](https://i.imgur.com/cFC8G9Z.png)

4. 接著點擊藍色框框裡的新增檔案按鈕 
5. 建立test.py檔(名稱可自取)

![](https://i.imgur.com/cYMmsV1.png)
#### STEP 5 ： 套模板
```
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *


app = Flask(__name__)
# LINE BOT info
line_bot_api = LineBotApi('Channel Access token')
handler = WebhookHandler('Channel Secret')

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
    line_bot_api.reply_message(reply_token, TextSendMessage(text = message))

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)
```
#### 模板解釋
* 13、14行：要改成自己的Channel Access token以及Channel Secret（Channel Access token在Messaging API，Channel Secret在Basic settings）

![](https://i.imgur.com/u88h2LJ.png)

* 16~26行：指定在 /callback 通道上接收訊息，方法是 POST而callback()是為了要檢查連線是否正常其中`signature`是LINE官方提供用來檢查該訊息是否透過LINE官方APP傳送而`body`就是用戶傳送的訊息，並且是以JSON的格式傳送

![](https://i.imgur.com/NNAOc72.png)

* 28~35行：這邊是用來接收訊息的地方，特別注意到第35行的line_bot_api.reply_message()，它是回傳訊息的方法，而我們設定回傳的型態是文字(text)

![](https://i.imgur.com/f7MBiLP.png)

* 37~40行：這裡是指定我們的BOT執行的位置是在 `0.0.0.0:80`，接上前面所說的，我們的BOT會接收訊息的位置也就是`0.0.0.0:80/callback`

![](https://i.imgur.com/8jbPrc3.png)

#### STEP 6 ： 執行test.py檔
點擊右上角的三角形按鈕
![](https://i.imgur.com/BOpFOiY.png)
這樣一來，我們就已經完成鸚鵡的功能了，在第35行的位置
#### STEP 7 ： 進行實作
1. 開啟cmd
2. 移動路徑到資料夾中
3. 下`ngrok.exe http 80`指令
4. 按下enter

![](https://i.imgur.com/MFHzEMb.png)

5. 開啟另一個cmd
6. 移動路徑到資料夾中
7. 下`python test.py`指令
8. 按下enter

![](https://i.imgur.com/o4nP0Ho.png)

順利的話，應該會出現下方這兩個cmd畫面
![](https://i.imgur.com/MnY6SzI.png)

![](https://i.imgur.com/W0PDiqw.png)

你會發現現在我們有一個在0.0.0.0:80 上跑的python還有一個會將訊息導向localhost:80 上的webhook我們現在只需要讓LINE知道我們的webhook在哪裡就完成了!
#### STEP 8 ： Webhook設定
1. 回到Messaging API畫面
2. 在Webhook URL的地方點擊Edit按鈕
3. 改成在ngrok.exe上看到的網址（第二個Forwarding，複製到ngrok.io為止）
4. 最後加上/callback（不要忘記了）
![](https://i.imgur.com/Umk5PKd.png)

點擊Update跟Verify後應該會出現Success

![](https://i.imgur.com/DlOlXuy.png)

這樣我們的鸚鵡式LINE機器人就建立成功拉
#### STEP 9 ： 把機器人加入好友並測試
1. 滑到Messaging API的上方
2. 輸入ID或掃QR code將機器人加入好友
3. 輸入你想說的話

![](https://i.imgur.com/JDijgIq.jpg)
恭喜完成LINE BOT的建置~
## Connect LINE BOT with Raspberry Pi
#### STEP 1 ： 開啟Rpi裡的瀏覽器，搜尋並下載ngrok
![](https://i.imgur.com/wQViPjR.png)
#### STEP 2 ： 到Downloads資料夾打開ngrok的壓縮檔
![](https://i.imgur.com/S6eQsFz.png)
#### STEP 3 ： 找到裡面的ngrok執行檔
![](https://i.imgur.com/1qI6Bgd.png)
#### STEP 4 ： 複製到與專案資料夾同一層的路徑
![](https://i.imgur.com/6Bypb5Q.png)
#### STEP 5 ： 下載LINE官方的Python套件
1. 開啟Rpi的terminal
2. 輸入`sudo pip3 install line-bot-sdk `
3. 等待安裝程序結束
#### STEP 6 ： 在專案資料夾中新建一個LINE BOT模板的py檔
![](https://i.imgur.com/gecl4qW.png)
> 注意：記得更改Channel Access token與Channel Secret，且檔名不要取作`linebot.py`
#### STEP 7 ： 啟動ngrok
1. 開啟另一個terminal
2. 移動至專案資料夾的路徑
3. 輸入`./ngrok http 80`

![](https://i.imgur.com/iOO88rT.jpg)
#### STEP 8 ： 執行剛剛建立的模板py檔
1. 移動至專案資料夾
2. 執行模板py檔
3. 輸入密碼

![](https://i.imgur.com/cn6vuK9.png)


#### STEP 9 : 複製ngrok執行檔第二個Forwarding路徑
![](https://i.imgur.com/uRAC4Ry.png)

> 注意：不能使用快捷鍵`ctrl+c`進行複製，這會結束ngrok的執行，因此要採用點擊右鍵，然後選擇Copy的方式複製
#### STEP 10 :  貼上並更新Webhook URL的路徑
![](https://i.imgur.com/jB1SQqI.png)
#### STEP 11 : Verify執行驗證
![](https://i.imgur.com/GuVcPkH.png)
#### STEP 12 : 跟機器人再聊天一次吧
![](https://i.imgur.com/bCseuTM.png)

這樣就完成與Raspberry Pi的串接了，可以因應需求在模板裡做進一步的延伸了~
## Connect LINE BOT with Raspberry Pi Example
```
import time
import sys

EMULATE_HX711 = False

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
    
    if not EMULATED_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()
    
hx_1 = HX711(17, 27)

hx_1.set_reading_format("MSB", "MSB")

hx_1.set_reference_unit(referenceUnit)

hx_1.reset()

hx_1.tare()

print("Tare done! Add weight now...")

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
            Try:
                val_1 = hx_1.get_weight(5)
                numOf_1 = round((abs(val_1 - 0.0) / 4.0))
                print("1NTD:%d" %numOf_1)
                print("total:", numOf_1*1)

                hx_1.power_down()

                hx_1.power_up()
                time.sleep(0.1)
            
            except (keyboardInterrupt, SystemExit):
                cleanAndExit()
        
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)
```
#### [VIDEO](https://youtu.be/zMhlQMEvxwI)
## What Piggy Banky Looks Like

![](https://i.imgur.com/aaa3W27.jpg)

## Demo Video
* [HX711 NTD50](https://youtu.be/f4cXLr8uTT8)
    * Calculate the number and price of NTD50 
    * `_50.py`
* [HX711 NTD10](https://youtu.be/Z0aRjCCHSYs)
    * Calculate the number and price of NTD10
    * `_10.py`
* [HX711 NTD5](https://youtu.be/8ucCzu58t0I)
    * Calculate the number and price of NTD5
    * `_5.py`
* [HX711 NTD1](https://youtu.be/DPkNIDD49mc)
    * Calculate the number and price of NTD1
    * `_1.py`
* [HX711 NTD1(Connected with LINE BOT)](https://youtu.be/zMhlQMEvxwI)
    * Calculate the number and price of NTD1(control by LINE BOT)
    * `linebot_1.py`
## Reference
[HX711 Python Library](https://github.com/tatobari/hx711py)\
[Build a digital Raspberry Pi Scale (with Weight Sensor HX711)](https://tutorials-raspberrypi.com/digital-raspberry-pi-scale-weight-sensor-hx711/)\
[Connecting 4 HX711 to one Raspberry Pi](https://raspberrypi.stackexchange.com/questions/96422/connecting-4-hx711-to-one-raspberry-pi)\
[HX711 with a Four Wire Load Cell and Arduino | Step by Step Guide](https://www.youtube.com/watch?v=sxzoAGf1kOo&t=382s)\
[LINE BOT Tutorial](https://ithelp.ithome.com.tw/users/20122649/ironman/3122)
