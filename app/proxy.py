#!/usr/bin/python
# -*- coding: UTF-8 -*-
# coding:utf-8

import sys
#sys.path.append("..")
import itchat
#import grouprobot
import time
import urllib2
import urllib
import json
import re
from itchat.content import *


reload(sys)
sys.setdefaultencoding("utf-8")


server_config = {}
gBlackListCache = []
gGroupMsgBuffer = {}

def http_register():
    url='http://weixin8.xiaoheqingting.com/app/index.php?i=1&c=entry&event_id=1&do=robotregister&m=xc_huoma'
    response = urllib2.urlopen(url)
    raw_resp = response.read()
    json_resp = json.loads(raw_resp)
    if (json_resp['status'] == 'OK') :
        server_config['endpoint'] = json_resp['endpoint']
        server_config['group'] = json_resp['group']
        print "Register success", server_config
    else:
        print "Fail register. Server return status %s" % (json_resp['status'])
        sys.exit()

http_register()

def hook_process_values(values) :
    return grouprobot.process(values)

def http_post(values):
    # return hook_process_values(values)

    if not server_config.has_key('endpoint') or server_config['endpoint'] == None:
        return None
    url= server_config['endpoint'] # 'http://weixin8.xiaoheqingting.com/app/index.php?i=1&c=entry&event_id=1&do=robotregister&m=xc_huoma'
    jdata = json.dumps(values)             # 对数据进行JSON格式化编码
    req = urllib2.Request(url, jdata)       # 生成页面请求的完整数据
    response = urllib2.urlopen(req)       # 发送页面请求
    return json.loads(response.read())


def inst_remove_blacklist_member(msg, blackList) :
    if 'Note' == msg['Type']  and 10000 == msg['MsgType'] :
        print u"有用户扫码入群，入群消息为：%s" % (msg['Text'])
        NoteNickName = re.findall(r"\"(.+)\"%s" % (u"通过扫描你分享的二维码加入群聊"), msg['Text'])
        if len(NoteNickName) == 1 :
            print u"有用户扫码入群，入群用户为：%s" % (NoteNickName[0])
            for k, b in blackList.iteritems():
                if b['NickName'] == NoteNickName[0]:
                    target.append({'UserName' : b['UserName']})
                    print u"用户命中缓存黑名单，立即删除: %s:%s" % (b['NickName'], b['UserName'])
            if len(target) >= 1:
                msg.user.delete_member(target)
    return 1


def remove_blacklist_member(chatroom, blackList) :
    memberList = chatroom['MemberList']
    target = []
    for one in memberList:
        for k, b in blackList.iteritems():
            if one['UserName'] == b['UserName'] or one['NickName'] == b['NickName'] :
                target.append(one)
                print u"用户命中缓存黑名单，捎带删除: %s:%s" % (one['UserName'], one['NickName'])
    if len(target) >= 1 :
        itchat.delete_member_from_chatroom(chatroom['UserName'], target)

    return 0



@itchat.msg_register([TEXT, NOTE], isGroupChat=True)
def text_reply(msg):
    global gBlackListCache
    if not server_config.has_key('group') or server_config['group'] == None:
        print "invalid server config"
        return
    if hasattr(msg['User'], 'NickName') and msg['User'].NickName.find(server_config['group']) < 0 :
        return

    xMsg = {}
    xMsg['Type']          = msg['Type']
    xMsg['MsgType']       = msg['MsgType']
    xMsg['GroupUserName'] = msg['User'].UserName
    xMsg['GroupNickName'] = msg['User'].NickName
    xMsg['Text']          = msg['Text']
    xMsg['FromUserName']  = msg['ActualUserName']
    xMsg['FromNickName']  = msg['ActualNickName']
    xMsg['GroupMembers']  = []

    needSendBatchMsgToRobot = False

    print u"群成员列表提取成功："
    for u in msg['User'].MemberList :
        xMsg['GroupMembers'].append({"UserName" : u.UserName, "NickName" : u.NickName})
        print u" %s %s" % (u.UserName, u.NickName)

    append_to_msg_buf(xMsg)

    print u"%s 在群[%s]里说: %s" % (xMsg['FromNickName'], xMsg['GroupNickName'], xMsg['Text'])


    enableQuickRemoveBlacklist = False # 暂时关闭本功能，避免封号。后面再细化对某些特殊用户施加本法术
    if gBlackListCache and enableQuickRemoveBlacklist :
        for k, v in gBlackListCache.iteritems():
            print u"缓存黑名单：%s %s" % (v['UserName'], v['NickName'])
        if 1 == inst_remove_blacklist_member(msg, gBlackListCache) :
            print u"刚刚进来，删掉了，直接返回"
            return

    return

    #if chatroom and (msg.isAt or msg.text.find(u'测试机器人') >= 0):
        #chatrooms = itchat.search_chatrooms(name=u'淘宝黑车')
        #chatroom = itchat.update_chatroom(chatrooms[0]['UserName'])
        #print len(chatroom['MemberList'])
        #msg.user.send(u'@%s\u2005 你喊我干啥? %s? 噢，对啦，咱们这个群里一共有%d个人了，等会儿切群，我来操作。' % (
        #    msg.actualNickName, msg.text, len(chatroom['MemberList'])))

def append_to_msg_buf(xMsg) :
    global gGroupMsgBuffer
    key = xMsg['GroupUserName']
    if not gGroupMsgBuffer.has_key(key) :
        gGroupMsgBuffer[key] = [xMsg]
    else :
        gGroupMsgBuffer[key].append(xMsg)
    return


## TODO: call human_simulator in a loop
def human_simulator() :
    global gGroupMsgBuffer
    gStop = False
    # 每次阅读一个 Group 的信息并处理。具体处理操作见 batch_process_group_msg，包括：
    # 1. 向 AI 逻辑发送群消息
    # 2. 获取回复意见
    # 3. 将回复发送到群里
    # 4. 在 batch_process_group_msg 内部 sleep 一段时间
    while True and not gStop and gGroupMsgBuffer:
        (groupUserName, batchMsg) = gGroupMsgBuffer.popitem()
        batch_process_group_msg(groupUserName, batchMsg)


def update_local_black_list(blacklist) :
    global gBlackListCache
    gBlackListCache = blacklist
    return

def batch_process_group_msg(groupUserName, batchMsg) :
    ep_resp = http_post(batchMsg)
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


class Member:
    def __init__(self, UserName, NickName):
        self.UserName = UserName
        self.NickName = NickName

class User:
    def __init__(self, UserName, NickName):
        self.UserName = UserName
        self.NickName = NickName
        self.MemberList = [Member("@yx", "jasimin"), Member("@yh", "raywill")]

msg = {'Type' : 'Text', 'MsgType' : 1, 'User' : User("@abc", u"淘宝联盟"), 'Text' : '空气 Hi Ray', 'ActualUserName' : '@yx', 'ActualNickName' : 'jasimin'}
msg2 = {'Type' : 'Text', 'MsgType' : 1, 'User' : User("@xyz", u"淘宝大学"), 'Text' : '空气 Hi Jasimin', 'ActualUserName' : '@yh', 'ActualNickName' : 'raywill'}
msg3 = {'Type' : 'Text', 'MsgType' : 1, 'User' : User("@xyz", u"淘宝大学"), 'Text' : '空气 Hi All', 'ActualUserName' : '@yh', 'ActualNickName' : 'raywill'}
text_reply(msg)
text_reply(msg2)
text_reply(msg3)
human_simulator()

#itchat.auto_login(True)
#itchat.run(True)
