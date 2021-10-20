import redis


class RedisLock(object):
    def __init__(self, key, service, host='127.0.0.1', port='6379', db=9, **kwargs):
        self.rdcon = self.argsinit(host, port, db, kwargs)
        self._lock = 0
        self.lock_key = key
        self.service = service

    def argsinit(self, host, port, db, kwwargs):
        if kwwargs:
            if kwwargs.get('password'):
                return redis.Redis(host, port, db, kwwargs['password'])
        return redis.Redis(host, port, db)

    @staticmethod
    def get_lock(cls):
        if cls.rdcon.exists(cls.lock_key) == 0:
            cls.rdcon.set(cls.lock_key, cls.service)
            cls._lock = 1
            return None
        return cls.rdcon.get(cls.lock_key)


def deco(cls):
    def _deco(func):
        def __deco(*args, **kwargs):
            return func(lock=cls.get_lock(cls), *args, **kwargs)

        return __deco

    return _deco
