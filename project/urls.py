from django.contrib import admin
from django.urls import path

from .apps.deals.views import Deals

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Deals.as_view())
]
