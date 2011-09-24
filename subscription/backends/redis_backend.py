from redis import Redis as RedisBase
import json
import time
import datetime

from subscription import backends

class Redis(RedisBase):
    def __init__(self,**kwargs):
        from django.conf import settings
        super(Redis,self).__init__(host=settings.REDIS_HOST,port=settings.REDIS_PORT,db=settings.REDIS_DB,**kwargs) 

class RedisBackend(backends.BaseBackend):
    def emit(self,*args,**kwargs):
        self.send_time = time.mktime(datetime.datetime.now().timetuple())
        super(RedisBackend,self).emit(*args,**kwargs)

    def user_emit(self,user,text):
        conn = Redis()
        conn.lpush("actstream::%s::undelivered" % user.pk,json.dumps((self.send_time,text)))
