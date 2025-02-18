import redis
import json
import threading
import time
from django.core.cache import cache
from django.conf import settings

from .utils import send_email


class SendEmailMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.redis_client = redis.from_url(settings.CACHES["default"]["LOCATION"])
        self.start_thread()
        
    def __call__(self, request):
        response = self.get_response(request)
        return response

    def start_thread(self):
        self.thread = threading.Thread(target=self.redis_worker)
        self.thread.daemon = True
        self.thread.start()

    def redis_worker(self):
        while True:
            try:
                while True:
                    task = self.redis_client.lpop('snippets_list')
                    if not task:
                        break

                    task = json.loads(task)
                    subject = 'Snippet "' + task["snippet_name"] + '" created successfully'
                    send_email(
                        subject=subject,
                        recipient_list=[task["sent_to"]],
                        template='email/snippet_mail.html',
                        context={
                            "snippet_name": task["snippet_name"],
                            "snippet_description": task["snippet_description"],
                            "username": task["username"],
                        }
                    )
                    print("Email enviado: ", task)
                
            except Exception as e:
                print("ERROR: ", e)

            time.sleep(60)
