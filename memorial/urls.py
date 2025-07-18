
from django.urls import path
from .views import (
    index,
)

app_name = 'memorials'

urlpatterns = [
    # Basic Pages
    path('', index, name='index'),

]