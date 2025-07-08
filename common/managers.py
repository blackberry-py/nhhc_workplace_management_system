import json

from django.conf import settings
from django.core.cache import cache
from django.core.serializers import deserialize, serialize
from django.db.models import QuerySet
from loguru import logger


class CachedQuerySet(QuerySet):
    def queryset_from_cache(self, filterdict=None):
        if filterdict is None:
            filterdict = {}
        # Generate a cache key based on the model name
        cachekey = str(self.model.__name__).lower()

        # Attempt to retrieve the queryset from the cache
        queryset = cache.get(cachekey)
        self.model.objects.all()

        if queryset:
            logger.debug(f"Cache Hit On Queryset for {cachekey}")
            logger.debug(type(queryset))
            cache_hit_queryset = queryset
            # If the queryset is found in the cache, return it with a flag indicating it was cached
            # data = {
            #     'in_cache': True,
            #     'queryset': queryset
            #     }
            # query = self.data['ps']]
            # Use Django's serialization instead of pickle for security
            try:
                deserialized_data = json.loads(cache_hit_queryset)
                return [obj.object for obj in deserialize("json", deserialized_data)]
            except (json.JSONDecodeError, ValueError):
                logger.warning(f"Failed to deserialize cached queryset for {cachekey}")
                # Fall through to fresh query

        # Cache miss or deserialization failed - generate fresh query
        logger.debug(f"Cache Miss On Queryset for {cachekey}, Setting In Cache")
        logger.debug(type(queryset))
        # If the queryset is not found in the cache, generate it from the database and store it in the cache
        fresh_query = self.model.objects.filter(**filterdict)
        # Use Django's serialization instead of pickle for security
        try:
            serialized_data = serialize("json", fresh_query)
            cache.set(cachekey, json.dumps(serialized_data), settings.QUERYSET_TTL)
        except Exception as e:
            logger.warning(f"Failed to serialize queryset for caching: {e}")
        return fresh_query

    queryset_from_cache.queryset_only = False
