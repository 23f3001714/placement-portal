from flask_redis import FlaskRedis
import json

redis = FlaskRedis(decode_responses=True)

def cache_get(key):
    data = redis.get(key)
    return json.loads(data) if data else None

def cache_set(key, value, ex):
    redis.set(key, json.dumps(value), ex=ex)

def cache_delete(*keys):
    redis.delete(*keys)