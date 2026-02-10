from django.urls import path
from ninja import NinjaAPI

from pybotx import DjangoNinjaAdapter
from example.todo_bot_django.bootstrap import bot, settings


api = NinjaAPI()
adapter = DjangoNinjaAdapter(bot, verify_requests=settings.verify_requests)
api.add_router("", adapter.router)

urlpatterns = [
    path("", api.urls),
]
