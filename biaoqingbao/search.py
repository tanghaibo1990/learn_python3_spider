#-*- coding:UTF-8 -*-
import glob
import time

import itchat
from itchat.content import TEXT, PICTURE


imgs = []

def searchImage(text):
    print('收到关键词: ', text)
    path = 'E:/biaoqingbao/'
    # path = '/home/wistbean/biaoqingbao/'
    for name in glob.glob(path + '*'+text+'*.jpg'):
        imgs.append(name)


@itchat.msg_register([PICTURE, TEXT])
def text_reply(msg):
    searchImage(msg.text)
    for img in imgs[:6]:
        msg.user.send_image(img)
        time.sleep(0.3)
        print('开始发送表情： ', img)
    imgs.clear()


itchat.auto_login(hotReload=True)
itchat.run()
