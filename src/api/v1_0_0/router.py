"""
Router file which handles routing for account
and groups and logout
"""
from django.conf.urls import url
from django.urls import (include,)
from rest_framework import routers
from . import views


__all__ = ['urlpatterns', ]

ROUTER = routers.SimpleRouter(trailing_slash=True)
ROUTER.register(r'users', views.UserViewSet, base_name='user')
ROUTER.register(r'logout', views.LogoutViewSet, base_name='logout')
ROUTER.register(r'groups', views.GroupViewSet, base_name='groups')
ROUTER.register(r'contacts', views.ContactViewSet, base_name='contact')

urlpatterns = [
    url(r'', include(ROUTER.urls)),
]
