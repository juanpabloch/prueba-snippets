import redis
import json
from django.core.cache import cache
from django.conf import settings


class SendEmailMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.redis_client = redis.from_url(settings.CACHES["default"]["LOCATION"])

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        response = self.get_response(request)

        # Code to be executed for each request/response after the view is called.
        
        # subject = 'Snippet "' + self.snippet.name + '" created successfully'
        print("Middleware!!!!")
        # data_list = json.loads(cache.get_many(cache.keys("snippets_*")))
        # keys = self.redis_client.keys("snippets_*")
        # data_list = self.redis_client.mget(keys)
        
        # snippets = [json.loads(item) for item in data_list if item]
        data_list = self.redis_client.lrange("snippets_list", 0, -1)
        snippets = [json.loads(item) for item in data_list]
        print("CACHE_LIST: ", snippets)

        # data = json.loads(cache.get("snippets"))
        # print("CACHE: ", data)
        # send_email(
            #     subject=subject,
            #     recipient_list=[snippet.user.email],
            #     template='email/snippet.html',
            #     context={
            #         "user": snippet.user,
            #         "snippet": snippet,
            #     }
            # )

        return response