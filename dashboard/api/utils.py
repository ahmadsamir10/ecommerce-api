from django.core.cache import cache



def set_cache_if_exists(key, add=None, remove=None, qs=None):
    if cache.get(key) != None:
        if add:
            return cache.incr(key, add)
        elif remove:
            return cache.decr(key, remove)
        elif qs:
            return cache.set(key, qs)