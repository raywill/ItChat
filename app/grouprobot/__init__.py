#!/usr/bin/python
# -*- coding: UTF-8 -*-
# coding:utf-8

import sys 
import time
import random
import threading

sys.path.append("../..")
import itchat

class GroupState():
    def __init__(self):
        return


class Core(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.gGroupMsgBuffer = []
        self.gGroupState = None
        self.gQRState = {"QRMediaId" : None, "QRMediaIdTs" : 0, "QRMediaFile" : "images/qr.png"}
        self.groupNickName = None
        self.groupUserName = None
        return

    def activateGroup(self, groupNickName, groupUserName) :
        if groupNickName != self.groupNickName :
            self.gGroupState = {"lastVerifyMsgTs" : 0, "lastWelcomeMsgTs" : 0, "curMemberCnt" : 0, "lastMemberCnt" : 0}
        self.groupNickName = groupNickName
        self.groupUserName = groupUserName

    def loadState(self) :
        # TODO: load group state from network
        return

    def run(self) :
        while True :
            self.process(itchat)

    def receive(self, xMsg):
        # 1. 找到群
        # 2. 对话记录到群对话记录里
        if self.gGroupState == None :
            self.activateGroup(xMsg['GroupNickName'], xMsg['GroupUserName'])

        if xMsg['GroupNickName'] != self.groupNickName :
            return

        self.gGroupMsgBuffer.append(xMsg)

        self.gGroupState['curMemberCnt'] = len(xMsg['GroupMembers'])

        print "grouprobot recieve a msg and saved to MsgBuffer"
        return

    def process(self, itchat):
        if self.gGroupState == None :
            return
        # TODO: 1. 看看哪些群到了回复消息的时间了；
        #       2. 分析 MsgBuffer 中的消息，予以自动回复
        got_reply = False
        if self.replied_with_text_rand(itchat, self.groupUserName) :
            got_reply = True
        elif self.replied_with_text_welcome(itchat, self.groupUserName) :
            got_reply = True
        elif self.replied_with_text_verify(itchat, self.groupUserName) :
            got_reply = True

        if not got_reply :
            print self.gGroupState
        time.sleep(random.randint(10, 16))
        return


    def upload_qr_if_required(self, itchat) :
        if time.time() - self.gQRState['QRMediaIdTs'] > 60 * 60 * 24 and None != self.gQRState['QRMediaFile']:
            r = itchat.upload_file(self.gQRState['QRMediaFile'], isPicture = True)
            if r :
                self.gQRState['QRMediaIdTs'] = time.time()
                self.gQRState['QRMediaId'] = r['MediaId']
        else :
            print 'Use cache %s' % (self.gQRState['QRMediaId'])


    def replied_with_text_welcome(self, itchat, groupUserName) :
        # 如果群人数有变化，并且距离上次发送消息
        if (((time.time() - self.gGroupState['lastWelcomeMsgTs'] > random.randint(60, 80)) and
            (self.gGroupState['lastMemberCnt'] != self.gGroupState['curMemberCnt']) and
            (self.gGroupState['curMemberCnt'] < 10)) or
            ((time.time() - self.gGroupState['lastWelcomeMsgTs'] > random.randint(180, 240)) and
                (self.gGroupState['curMemberCnt'] < 10))):
            if (self.gGroupState['lastMemberCnt'] != self.gGroupState['curMemberCnt']) :
                itchat.send(u'%s' % (u'请新入群同学请手工拉好友入群，或找群主要二维码发到朋友圈，并截图'), toUserName = groupUserName)
            else :
                itchat.send(u'%s' % (u'群里的同学们积极点转发朋友圈啊，人数不够不开始。二维码快转起来~~。好了截图发群里。'), toUserName = groupUserName)
            time.sleep(random.randint(10, 15))
            self.upload_qr_if_required(itchat)
            if self.gQRState['QRMediaIdTs'] > 0:
                itchat.send_image(self.gQRState['QRMediaFile'], mediaId = self.gQRState['QRMediaId'], toUserName = groupUserName)
            else:
                print "QRMediaIdTs is zero"

            self.gGroupState['lastMemberCnt'] = self.gGroupState['curMemberCnt']
            self.gGroupState['lastWelcomeMsgTs'] = time.time()
            return True
        else :
            return False

    def replied_with_text_verify(self, itchat, groupUserName) :
        # 如果群人数有变化，并且距离上次发送消息
        if ((time.time() - self.gGroupState['lastVerifyMsgTs'] > random.randint(20, 40)) and
                (self.gGroupState['curMemberCnt'] >= 10)):
            itchat.send(u'%s' % (u'同学，请发朋友圈截图。@某某 你的格式正确，已经认证成功。'), toUserName = groupUserName)
            self.gGroupState['lastVerifyMsgTs'] = time.time()
            return True
        else :
            return False

    def replied_with_text_rand(self, itchat, groupUserName):
      wait_enough = True
      r = random.randint(1, 20)
      if 1 == r and wait_enough:
        itchat.send(u'%s' % ([u"啊~", u"喵", u"🙃", u"😭", u"😭", u"😁"][random.randint(0,5)]), toUserName = groupUserName)
        return True
      else :
        return False


def new_instance():
    newInstance = Core()
    return newInstance

originInstance = new_instance()

process = originInstance.process
receive = originInstance.receive
start   = originInstance.start
