from app import redisClient
import datetime

for i in range(1000,9999):
    redisClient.hset(str(i), "id", i)
    redisClient.hset(str(i), "timestamp", datetime.datetime.now().strftime('%Y%m%d%H%M%S'))

print redisClient.hget('2999','id'),redisClient.hget('2999','timestamp')