#!/usr/bin/python
# -*- coding: UTF-8 -*-
# coding:utf-8

import sys
import itchat, time
from itchat.content import *
import time, easygui

easygui.msgbox("别忘了打卡！", title="提醒",ok_button="知道啦")

reload(sys)
sys.setdefaultencoding("utf-8")


@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
    msg.user.send('%s: %s' % (msg.type, msg.text))

@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def download_files(msg):
    msg.download(msg.fileName)
    typeSymbol = {
        PICTURE: 'img',
        VIDEO: 'vid', }.get(msg.type, 'fil')
    return '@%s@%s' % (typeSymbol, msg.fileName)

@itchat.msg_register(FRIENDS)
def add_friend(msg):
    msg.user.verify()
    msg.user.send('Nice to meet you!')

@itchat.msg_register(TEXT, isGroupChat=True)
def text_reply(msg):
    print "from %s: %s" % (msg.actualNickName, msg.text)
    if msg.isAt:
        chatrooms = itchat.search_chatrooms(name=u'淘宝黑车')
        chatroom = itchat.update_chatroom(chatrooms[0]['UserName'])
        print len(chatroom['MemberList'])
        msg.user.send(u'@%s\u2005 你喊我干啥? %s? 噢，对啦，咱们这个群里一共有%d个人了，等会儿切群，我来操作。' % (
            msg.actualNickName, msg.text, len(chatroom['MemberList'])))

itchat.auto_login(True)
itchat.run(True)
