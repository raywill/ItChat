
def run(f):
  f("gogo")

def register_msg():
  print "begin register"
  return run

@register_msg()
def text_reply(msg):
  print msg

'''
1. register_msg is called and return a functor
2. functor called with registered function as param
'''

