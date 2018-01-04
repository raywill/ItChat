#!/usr/bin/python
# -*- coding: UTF-8 -*-
# coding:utf-8

import time
import random

class Core(object):
    def __init__(self):
        self.gGroupMsgBuffer = {}
        return
    def receive(self, xMsg):
        # 1. 找到群
        # 2. 对话记录到群对话记录里
        key = xMsg['GroupUserName']
        if not self.gGroupMsgBuffer.has_key(key) :
            self.gGroupMsgBuffer[key] = [xMsg]
        else :
            self.gGroupMsgBuffer[key].append(xMsg)
        print self.gGroupMsgBuffer
        print "grouprobot recieve a msg and saved to MsgBuffer"
        return

    def process(self, itchat):
        result = {"msg" : "Local module handler"}
        # TODO: 1. 看看哪些群到了回复消息的时间了；
        #       2. 分析 MsgBuffer 中的消息，予以自动回复
        got_reply = False
        for groupUserName, batchMsg in  self.gGroupMsgBuffer.items():
          if self.replied_with_text_rand(itchat, groupUserName):
            got_reply = True
            break
          if self.replied_with_text_1(groupUserName, batchMsg):
            got_reply = True
            break
          if self.replied_with_text_2(groupUserName, batchMsg):
            got_reply = True
            break
          if self.replied_with_text_3(groupUserName, batchMsg):
            got_reply = True
            break

        if not got_reply :
            print "..."
        time.sleep(random.randint(1, 6))

        return

    def replied_with_text_1(self, groupUserName, batchMsg):
      # 如果群人数有变化，并且距离上次发送消息
      return False
    def replied_with_text_2(self, groupUserName, batchMsg):
      return False
    def replied_with_text_3(self, groupUserName, batchMsg):
      return False
    def replied_with_text_4(self, groupUserName, batchMsg):
      return False

    def replied_with_text_rand(self, itchat, groupUserName):
      wait_enough = True
      r = random.randint(1,3)
      if 1 == r and wait_enough:
        itchat.send(u'%s' % ([u"🙃", u"😭", u"😭", u"😁"][random.randint(0,3)]), toUserName = groupUserName)
        return True
      else :
        return False


    def batch_process_group_msg(self, itchat, groupUserName, batchMsg) :
        ep_resp = {"msg" : "Local module handler"}

        print "batch process group %s, which has %d msg" % (groupUserName, len(batchMsg))

        if None != ep_resp :

            if ep_resp.has_key('msg') and ep_resp['msg'] :
                itchat.send(u'%s' % (ep_resp['msg']), toUserName = groupUserName)

            if ep_resp.has_key('image') and ep_resp['image'] :
                print "send image to QQ", ep_resp['image']
                # msg.user.send_image(ep_resp['image']);



def new_instance():
    newInstance = Core()
    return newInstance

originInstance = new_instance()

process = originInstance.process
receive = originInstance.receive
