



import config
import redis


r = redis.StrictRedis(host=config.redis_host, port=config.redis_port)


