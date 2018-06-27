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
import gspread
from oauth2client.service_account import ServiceAccountCredentials as SAC
import time
import datetime


GDriveJSON = 'LinebotUpload.json'
GSpreadSheet = 'LinebotUpload'

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
    correct_right_now = datetime.datetime.now() + datetime.timedelta(hours=8)

    scope = ['https://www.googleapis.com/auth/drive']
    key = SAC.from_json_keyfile_name(GDriveJSON, scope)
    gc = gspread.authorize(key)
    worksheet = gc.open(GSpreadSheet).sheet1


    if(event.message.type == 'text'):
        worksheet.append_row((correct_right_now.strftime('%Y/%m/%d %H:%M'), event.message.type, event.message.text,event.source.user_id))


        if(event.message.text=="安安"):
            message = TextSendMessage(text='安安')
            line_bot_api.reply_message(event.reply_token, message)
        if(event.message.text[0]=="抽"):
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



    elif(event.message.type == 'location'):
        lat = event.message.latitude
        lng = event.message.longitude
        worksheet.append_row((correct_right_now.strftime('%Y/%m/%d %H:%M'), event.source.user_id, lat, lng))


        r = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+repr(lat)+','+repr(lng)+'&radius=400&type=restaurant&language=zh-TW&key=AIzaSyBeL3-P6F9yGg27Vns0c6e65-cIFqkhFcA')
        r.encoding = 'utf-8'
        time.sleep(1)
        repeat=0
        j=[]
        j.append(json.loads(r.content))
        endj = j[0]['results']
        while(repeat<100):
            if 'next_page_token' in j[repeat]:
                repeat+=1
            else:
                break
            nextpageid=j[repeat-1]['next_page_token']
            time.sleep(1)
            r = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken=' + nextpageid + '&language=zh-TW&key=AIzaSyBeL3-P6F9yGg27Vns0c6e65-cIFqkhFcA')
            j.append(json.loads(r.content))
            endj += j[repeat]['results']
        for i in range(0,len(endj)):
            if('rating' not in endj[i]):
                endj[i]['rating'] = 0.0
            if ('opening_hours' not in endj[i]):
                endj[i]['opening_hours'] = {'open_now': "營業狀況未知"}
            else:
                if (endj[i]['opening_hours']['open_now'] == True):
                    endj[i]['opening_hours']['open_now'] = "營業中"
                else:
                    endj[i]['opening_hours']['open_now'] = "未營業"

        endj = sorted(endj, key=lambda x: x['rating'])
        allname = ""
        for i in range(0, len(endj)-1):
            allname += str(i + 1) + "." + endj[i]['name'] + "  " + str(endj[i]['rating']) + "\n" + str(endj[i]['opening_hours']['open_now']) + "\n" +endj[i]['vicinity']+ "\n"+"\n"
        allname += str(len(endj)) + "." + endj[len(endj)-1]['name'] + "  " + str(endj[len(endj)-1]['rating']) + "\n" + str(endj[len(endj)-1]['opening_hours']['open_now'])+"\n"+endj[len(endj)-1]['vicinity']

        message = TextSendMessage(text=allname)
        line_bot_api.reply_message(event.reply_token, message)



    else:
        worksheet.append_row((correct_right_now.strftime('%Y/%m/%d %H:%M'), event.message.type, event.message.type, event.source.user_id))
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
