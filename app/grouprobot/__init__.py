#!/usr/bin/python
# -*- coding: UTF-8 -*-
# coding:utf-8


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

        return

    def process(self, itchat):
        result = {"msg" : "Local module handler"}
        while True self.gGroupMsgBuffer:
            (groupUserName, batchMsg) = self.gGroupMsgBuffer.popitem()
            batch_process_group_msg(itchat, groupUserName, batchMsg)


    def batch_process_group_msg(itchat, groupUserName, batchMsg) :
        ep_resp = {"msg" : "Local module handler"}

        print "batch process group %s, which has %d msg" % (groupUserName, len(batchMsg))

        if None != ep_resp :
            if ep_resp.has_key('blacklist') and ep_resp['blacklist']:
                update_local_black_list(ep_resp['blacklist'])
                chatroom = itchat.search_chatrooms(userName = groupUserName)
                if chatroom:
                    remove_blacklist_member(chatroom, ep_resp['blacklist'])

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
