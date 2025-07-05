from django.db import connection
from loguru import logger


class LogDatabaseQueriesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Log SQL queries after response is generated
        if connection.queries:
            for query in connection.queries:
                logger.log("DATABASE_QUERY", f"SQL Query: {query['sql']} | Time: {query['time']}s")
        return response
