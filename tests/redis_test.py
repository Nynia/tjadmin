import datetime
import redis
redisClient = redis.StrictRedis(host='localhost',port=6379,db=2)


print redisClient.hget('2999','id'),redisClient.hget('2999','timestamp')
print redisClient.dbsize(),redisClient.hlen('2999')
print redisClient.hexists('100','id')
print redisClient.hexists('1000','ids')
print redisClient.hget('100','id')