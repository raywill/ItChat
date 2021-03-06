#!/usr/bin/python
# -*- coding: UTF-8 -*-
# coding:utf-8

import sys
import oss2
import subprocess
import random
from PIL import Image
#sys.path.append("..")
import itchat
import grouprobot
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
    do_get_data(url)

def http_refresh():
    url='http://weixin8.xiaoheqingting.com/app/index.php?i=1&c=entry&event_id=1&do=robotrefresh&m=xc_huoma'
    do_get_data(url)

def http_upload_group_qr(groupName, filePath):
    url='http://weixin8.xiaoheqingting.com/app/index.php?i=1&c=entry&event_id=1&do=robotcreategroup&m=xc_huoma&%s&%s'
    g = {'groupname': groupName}
    f = {'url':filePath}
    response = urllib2.urlopen(url % (urllib.urlencode(g), urllib.urlencode(f)))
    print url % (urllib.urlencode(g), urllib.urlencode(f))
    raw_resp = response.read()
    print raw_resp
    json_resp = json.loads(raw_resp)
    if (json_resp['status'] == 'OK') :
        print "create group success", server_config
    else:
        print "Fail register. Server return status %s" % (json_resp['status'])


def do_get_data(url):
    global server_config
    response = urllib2.urlopen(url)
    raw_resp = response.read()
    json_resp = json.loads(raw_resp)
    if (json_resp['status'] == 'OK') :
        server_config['endpoint'] = json_resp['endpoint']
        server_config['group'] = json_resp['group']
        server_config['mode'] = json_resp['mode']
        print "get data success", server_config
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


@itchat.msg_register([PICTURE], isGroupChat=True)
def download_files(msg):
    if not server_config.has_key('group') or server_config['group'] == None:
        print "invalid server config"
        return
    if hasattr(msg['User'], 'NickName') and msg['User'].NickName.find(server_config['group']) < 0 :
        return
    if server_config['mode'] == 'setup':
        setup_group(msg)
    else:
        check_screenshot(msg)
    return

def check_screenshot(msg):
    f = msg.download(msg.fileName)
    print f
    print msg['FileName']
    time.sleep(random.randint(8, 16))
    try:
      img = Image.open(msg['FileName'])
      if img.size[0] == 750 and img.size[1] == 1160 :
        itchat.send(u'@%s %s' % (msg['ActualNickName'], u"请发送本海报到朋友圈才算报名成功哦!"), toUserName = msg['User'].UserName)
        return
    except IOError as e:
      print e
      pass

    try:
      out_bytes = subprocess.check_output(['zbarimg','-q','--raw', msg['FileName']]).decode('utf-8')
      if out_bytes.strip() == u'http://sh.52paipai.net.cn/5k/b/_.q/zyru/U/w/69//67EFqJTjCmqpc8VfAQAAOAQA71Ja' :
        itchat.send(u'@%s %s' % (msg['ActualNickName'], u"靠谱，图片是真的，认证通过。其他人加油!"), toUserName = msg['User'].UserName)
      else :
        print out_bytes.strip()
        print u'http://sh.52paipai.net.cn/5k/b/_.q/zyru/U/w/69//67EFqJTjCmqpc8VfAQAAOAQA71Ja'
        itchat.send(u'@%s %s' % (msg['ActualNickName'], u"请输入正确的截图, 我读书少，别骗我"), toUserName = msg['User'].UserName)
    except subprocess.CalledProcessError as e:
      out_bytes = e.output       # Output generated before error
      code      = e.returncode   # Return code
      print "fail exec with code %d" % (code)
      itchat.send(u'@%s %s' % (msg['ActualNickName'], u"什么图，看不清楚啊"), toUserName = msg['User'].UserName)

    return


def setup_group(msg) :
    f = msg.download(msg.fileName)

    endpoint = 'http://oss-cn-beijing.aliyuncs.com'
    auth = oss2.Auth('MpiECWThc6otZsVR', '9OEAnT0AHAcgeFLhu1G93e2qXHQQkt')
    bucket = oss2.Bucket(auth, endpoint, 'ftw')
    key = msg['FileName']
    with open(key, 'rb') as f:
        bucket.put_object(key, f)
    filePath = "%s/%s" % ("http://ftw.oss-cn-beijing.aliyuncs.com", key)
    http_upload_group_qr(msg['User'].NickName, filePath)

    time.sleep(random.randint(8, 16))
    itchat.send(u'@%s %s %s' % (msg['ActualNickName'], u"当前处于 setup 模式，你的图片已经作为群二维码提交到后台。", time.time()), toUserName = msg['User'].UserName)
    return


@itchat.msg_register([TEXT, NOTE], isGroupChat=True)
def text_reply(msg):
    global gBlackListCache
    if not server_config.has_key('group') or server_config['group'] == None:
        print "invalid server config"
        return
    if hasattr(msg['User'], 'NickName') and msg['User'].NickName.find(server_config['group']) < 0 :
        return

    xMsg = {}
    xMsg['Timestamp']     = time.time()
    xMsg['Type']          = msg['Type']
    xMsg['MsgType']       = msg['MsgType']
    xMsg['GroupUserName'] = msg['User'].UserName
    xMsg['GroupNickName'] = msg['User'].NickName
    xMsg['Text']          = msg['Text']
    xMsg['FromUserName']  = msg['ActualUserName']
    xMsg['FromNickName']  = msg['ActualNickName']
    xMsg['GroupMembers']  = []

    print u"群成员列表提取成功："
    for u in msg['User'].MemberList :
        xMsg['GroupMembers'].append({"UserName" : u.UserName, "NickName" : u.NickName})
        print u" %s %s" % (u.UserName, u.NickName)

    print u"%s 在群[%s]里说: %s" % (xMsg['FromNickName'], xMsg['GroupNickName'], xMsg['Text'])

    grouprobot.receive(xMsg)

    enableQuickRemoveBlacklist = False # 暂时关闭本功能，避免封号。后面再细化对某些特殊用户施加本法术
    if gBlackListCache and enableQuickRemoveBlacklist :
        for k, v in gBlackListCache.iteritems():
            print u"缓存黑名单：%s %s" % (v['UserName'], v['NickName'])
        if 1 == inst_remove_blacklist_member(msg, gBlackListCache) :
            print u"刚刚进来，删掉了，直接返回"
            return

    return

## TODO: call human_simulator in a loop
def human_simulator(cnt) :
    while cnt:
        eof = grouprobot.process(itchat)
        if eof:
          break
        cnt = cnt - 1


###
### TEST CODE BELOW
###
class Member:
    def __init__(self, UserName, NickName):
        self.UserName = UserName
        self.NickName = NickName

class User:
    def __init__(self, UserName, NickName, MemberList =  [Member("@yx", "jasimin"), Member("@yh", "raywill")]):
        self.UserName = UserName
        self.NickName = NickName
        self.MemberList = MemberList

msg = {'Type' : 'Text', 'MsgType' : 1, 'User' : User("@abc", u"淘宝联盟"), 'Text' : '空气 Hi Ray', 'ActualUserName' : '@yx', 'ActualNickName' : 'jasimin'}
msg2 = {'Type' : 'Text', 'MsgType' : 1, 'User' : User("@xyz", u"淘宝大学"), 'Text' : '空气 Hi Jasimin', 'ActualUserName' : '@yh', 'ActualNickName' : 'raywill'}
msg3 = {'Type' : 'Text', 'MsgType' : 1, 'User' : User("@xyz", u"淘宝大学"), 'Text' : '空气 Hi All', 'ActualUserName' : '@yh', 'ActualNickName' : 'raywill'}
msg4 = {'Type' : 'Text', 'MsgType' : 1, 'User' : User("@xyz", u"淘宝大学"), 'Text' : 'Clean Hi All', 'ActualUserName' : '@m3', 'ActualNickName' : 'm3'}
msg5 = {'Type' : 'Text', 'MsgType' : 1, 'User' : User("@abc", u"淘宝联盟", [Member("@yx", "jasimin"), Member("@yh", "raywill"), Member("@m3", "m3")]), 'Text' : 'Late wispery', 'ActualUserName' : '@cx', 'ActualNickName' : 'laugher'}

http_upload_group_qr(u"淘宝大家投", "http://weixin8.xiaoheqingting.com/attachment/images/1/2017/11/iw2XG4N777n7wJCwKOo8wj99HWnnnG.jpg")

text_reply(msg)
text_reply(msg2)
text_reply(msg3)
human_simulator(3)
text_reply(msg4)
text_reply(msg5)
human_simulator(3000)
'''
grouprobot.start()
itchat.auto_login(True)
itchat.run(True)
'''
