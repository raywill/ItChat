#!/usr/bin/python
# -*- coding: UTF-8 -*-
# coding:utf-8

import sys
sys.path.append("..")
import itchat, time
import urllib2
import urllib
import json
import re
from itchat.content import *


reload(sys)
sys.setdefaultencoding("utf-8")


server_config = {}
gBlackList = []

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


def http_post(values):
    if not server_config.has_key('endpoint') or server_config['endpoint'] == None:
        return None
    url= server_config['endpoint'] # 'http://weixin8.xiaoheqingting.com/app/index.php?i=1&c=entry&event_id=1&do=robotregister&m=xc_huoma'
    jdata = json.dumps(values)             # 对数据进行JSON格式化编码
    req = urllib2.Request(url, jdata)       # 生成页面请求的完整数据
    response = urllib2.urlopen(req)       # 发送页面请求
    return response.read()                    # 获取服务器返回的页面信息

def remove_blacklist_member(msg, chatroom, blackList) :
    memberList = chatroom['MemberList']
    target = []

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

    for one in memberList:
        for k, b in blackList.iteritems():
            if one['UserName'] == b['UserName'] or one['NickName'] == b['NickName'] :
                target.append(one)
                print "%s:%s is in blacklist. remove him" % (one['UserName'], one['NickName'])
    if len(target) >= 1 :
        msg.user.delete_member(target)

    return 0



@itchat.msg_register([TEXT, NOTE], isGroupChat=True)
def text_reply(msg):
    global gBlackList
    if not server_config.has_key('group') or server_config['group'] == None:
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

    for u in msg['User'].MemberList :
        xMsg['GroupMembers'].append({"UserName" : u.UserName, "NickName" : u.NickName})
        print u"群成员列表：%s %s" % (u.UserName, u.NickName)
    chatroom = itchat.search_chatrooms(userName = xMsg['GroupUserName'])
    print u"%s 在群[%s]里说: %s" % (xMsg['FromNickName'], xMsg['GroupNickName'], xMsg['Text'])

    if gBlackList:
        for k, v in gBlackList.iteritems():
            print u"缓存黑名单：%s %s" % (v['UserName'], v['NickName'])
        if 1 == remove_blacklist_member(msg, chatroom, gBlackList) :
            print u"刚刚进来，删掉了，直接返回"
            return

    json_resp = http_post(xMsg)
    print json_resp
    ep_resp = json.loads(json_resp)

    if None != ep_resp :
        if ep_resp['blacklist']:
            gBlackList = ep_resp['blacklist']
            remove_blacklist_member(msg, chatroom, gBlackList)

        if ep_resp['msg']:
            msg.user.send(u'%s' % (ep_resp['msg']))

        if ep_resp['image']:
            print "send image to QQ", ep_resp['image']
            # msg.user.send_image(ep_resp['image']);

    return

    #if chatroom and (msg.isAt or msg.text.find(u'测试机器人') >= 0):
        #chatrooms = itchat.search_chatrooms(name=u'淘宝黑车')
        #chatroom = itchat.update_chatroom(chatrooms[0]['UserName'])
        #print len(chatroom['MemberList'])
        #msg.user.send(u'@%s\u2005 你喊我干啥? %s? 噢，对啦，咱们这个群里一共有%d个人了，等会儿切群，我来操作。' % (
        #    msg.actualNickName, msg.text, len(chatroom['MemberList'])))

itchat.auto_login(True)
itchat.run(True)
