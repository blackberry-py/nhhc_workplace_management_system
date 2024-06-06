import pickle

from django.conf import settings
from django.core.cache import cache
from django.db.models import QuerySet
from loguru import logger


class CachedQuerySet(QuerySet):
    def queryset_from_cache(self, filterdict={}):
        # Generate a cache key based on the model name
        cachekey = str(self.model.__name__).lower()

        # Attempt to retrieve the queryset from the cache
        queryset = cache.get(cachekey)
        qself = self.model.objects.all()

        if queryset:
            logger.debug(f"Cache Hit On Queryset for {cachekey}")
            logger.debug(type(queryset))
            cache_hit_queryset = queryset
            # If the queryset is found in the cache, return it with a flag indicating it was cached
            # data = {
            #     'in_cache': True,
            #     'queryset': queryset
            #     }
            # query = qself.data['ps']]
            return pickle.loads(cache_hit_queryset)
        else:
            logger.debug(f"Cache Miss On Queryset for {cachekey}, Setting In Cache")
            logger.debug(type(queryset))
            # If the queryset is not found in the cache, generate it from the database and store it in the cache
            fresh_query = self.model.objects.filter(**filterdict)
            cache.set(cachekey, pickle.dumps(fresh_query), settings.QUERYSET_TTL)
            # data = {
            #     'in_cache': False,
            #     'queryset': queryset
            #     }
            # query = qself.data['ps']
            cache_miss_queryset = fresh_query
            return cache_miss_queryset

    queryset_from_cache.queryset_only = False
