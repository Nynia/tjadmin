import datetime
import redis
redisClient = redis.StrictRedis(host='localhost',port=6379,db=2)


print redisClient.hget('2999','id'),redisClient.hget('2999','timestamp')
print redisClient.dbsize()
print type(redisClient.hget('1000')),redisClient.hget('1000')