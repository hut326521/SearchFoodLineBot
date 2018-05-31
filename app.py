#-*- coding: UTF-8 -*-
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)
import requests
import json
import random
from bs4 import BeautifulSoup

class Rname(object):
    na = ""
    ra = 0
    op = ""
    newop = ""
app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('hl7jHmLtYnR2H1UCaxWhLv2TMs9Hnc8J1uB+ovJ4bUKm3/NP+0jwwRWIavmRb/RTXr9KPRNGXcZ+8znDb6Eg/Z/RYOXb9j+QuiRPY1Um75aFZrt8p3WVo+5zaHcFEzogSJ5N/dNeh4tNCECcTkEefQdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('7f1f42c9fcbb35f67deeae9cde99ded3')

@app.route("/", methods=['GET'])
def hello():
    return "Hello World!"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent)
def handle_message(event):
    if(event.message.type == 'text'):

        if(event.message.text=="安安"):
            message = TextSendMessage(text='安安')
            line_bot_api.reply_message(event.reply_token, message)
        elif(event.message.text[0]=="抽"):
            newm = event.message.text.strip('抽')
            newm = newm.strip()
            r = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/xml?query='+ newm +'&opennow=true&language=zh-TW&type=restaurant&key=AIzaSyBeL3-P6F9yGg27Vns0c6e65-cIFqkhFcA')
            r.encoding = 'utf-8'
            soup = BeautifulSoup(r.content, 'html.parser')
            rname = []
            for name in soup.find_all('name'):
                rname.append(name.text)
            luckyname = rname[random.randint(0, len(rname)-1)]



            message = TextSendMessage(text=luckyname)
            line_bot_api.reply_message(event.reply_token, message)


        else:
            message = TextSendMessage(text='好帥')
            line_bot_api.reply_message(event.reply_token, message)


    elif(event.message.type == 'location'):
        lat = event.message.latitude
        lng = event.message.longitude
        r = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/xml?location='+repr(lat)+','+repr(lng)+'&radius=500&type=restaurant&language=zh-TW&key=AIzaSyBeL3-P6F9yGg27Vns0c6e65-cIFqkhFcA')
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.content, 'html.parser')
        rname = Rname()
        rname.na = []
        rname.op = []
        rname.ra = []
        rname.newop = []
        a = 0
        for i in range(0, len(soup.find_all(['name', 'open_now']))):
            if ((soup.find_all(['name', 'open_now'])[i].text != "false" and soup.find_all(['name', 'open_now'])[i].text != "true")):
                a += 1
                if (a == 2):
                    rname.op.append("unknown")
                    a -= 1
                rname.na.append(soup.find_all(['name', 'open_now'])[i].text)
            else:
                rname.op.append(soup.find_all(['name', 'open_now'])[i].text)
                a = 0
        for rating in soup.find_all('rating'):
            rname.ra.append(rating.text)
        for i in range(0, len(rname.op)):
            if (rname.op[i] == "false"):
                rname.newop.append("未營業")
            elif (rname.op[i] == "true"):
                rname.newop.append("營業中")
            else:
                rname.newop.append("未知是否營業")

        allname = ""
        for i in range(0, len(rname.na) - 1):
            allname += str(i + 1) + "." + rname.na[i] + "  " + rname.ra[i] + "\n" + rname.newop[i] + "\n"+"\n"
        allname += str(len(rname.na)) + "." + rname.na[len(rname.na) - 1] + "  " + rname.ra[len(rname.ra) - 1] + "\n" + rname.newop[len(rname.newop) - 1]

        message = TextSendMessage(text=allname)
        line_bot_api.reply_message(event.reply_token, message)



    else:
        message = TextSendMessage(text=event.message.type)
        line_bot_api.reply_message(event.reply_token, message)









"""
message2 = ImageSendMessage(
    original_content_url='https://1.bp.blogspot.com/-GKiOtRUSOY0/UOh61ubADAI/AAAAAAAAAIE/pjvq0L9s-gA/s1600/IMG_2720.JPG',
    preview_image_url='https://1.bp.blogspot.com/-GKiOtRUSOY0/UOh61ubADAI/AAAAAAAAAIE/pjvq0L9s-gA/s1600/IMG_2720.JPG'
)
line_bot_api.reply_message(event.reply_token, message2)
"""







import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
