import redis


def db():
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
    return redis_client
