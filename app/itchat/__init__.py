#!/usr/bin/python
# -*- coding: UTF-8 -*-
# coding:utf-8


from . import content

class Core(object):
    def __init__(self):
        return
    def send(self, msg, toUserName):
        print "[to %s ] : %s" % (toUserName, msg)
        return
    def delete_member_from_chatroom(self, toUserName, users):
        print "delete_member_from_chatroom"
        return
    def search_chatrooms(self, userName) :
        print "search chatroom %s" % userName
        return None
    def msg_register(self, types, isGroupChat) :
        print "msg register"
 	def _msg_register(fn):
	        return fn
    	return _msg_register



def new_instance():
    newInstance = Core()
    return newInstance

originInstance = new_instance()

search_chatrooms            = originInstance.search_chatrooms
delete_member_from_chatroom = originInstance.delete_member_from_chatroom
send                        = originInstance.send
msg_register                = originInstance.msg_register
