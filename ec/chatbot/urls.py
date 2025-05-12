from django.urls import path
from .views import get_response

urlpatterns = [
    path('get-response/', get_response, name='get_response'),
]
