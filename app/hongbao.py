#!/usr/bin/python
# -*- coding: UTF-8 -*-
# coding:utf-8

import sys
import re
import itchat, time
from itchat.content import *

# -*- coding: UTF-8 -*-
# coding:utf-8

import sys
import re
import itchat, time
from itchat.content import *

reload(sys)
sys.setdefaultencoding("utf-8")

msgs=[]
logMsg=False

def process_text(nickName, msg):
  global msgs
  global logMsg
  if (msg == u'竞猜开始'):
    logMsg = True
    msgs = [] # clear previous round
  elif (msg == u'竞猜结束'):
    logMsg = False
  elif logMsg:
    searchObj = re.findall(r"\d+\.?\d*", msg)
    if searchObj:
      m = {"text":msg, "value": float(searchObj[-1]), "nick":nickName}
      msgs.append(m)

@itchat.msg_register(TEXT, isGroupChat=True)
def text_reply(msg):
  process_text(msg.actualNickName, msg.text)
  print msg.text

@itchat.msg_register([TEXT])
def text_reply(msg):
  global msgs
  #'RemarkName', 'NickName', 'Alias'
  print "[MSG] %s:%s:%s" % (msg.fromUserName, msg['User']['UserName'], msg.text)
  print "[CHECK EQUAL] %d" % (msg.text == u'统计')

  if (msg['User']['UserName'] == 'filehelper'):
    if (msg.text == u'统计'):
      refValue = 0
      refNick = None
      for x in msgs:
        if x['value'] > refValue :
          refValue = x['value']
          refNick = x['nick']

      print msgs
      print refValue
      print refNick

      if refNick:
        itchat.send_msg(u"优胜者%s %f" % (refNick, refValue), toUserName='filehelper')
      else:
        itchat.send_msg(u"未产生优胜者", toUserName='filehelper')
  else:
    itchat.send_msg(msg.text, toUserName='filehelper')

itchat.auto_login(True)
itchat.run(True)
