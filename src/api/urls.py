"""
URL file which redirect routing of 1.0.0
It is redirected to router file in v1.0.0 directory
"""
from django.urls import (path, include)

urlpatterns = [
    path(r'1.0.0/', include(('api.v1_0_0.router', 'api'), namespace='1.0.0')),
]
