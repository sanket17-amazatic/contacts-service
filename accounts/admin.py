'''
Registering AppUser, BlackListedToken model
'''
from django.contrib import admin
from .models import AppUser, BlackListedToken

class AppUserAdmin(admin.ModelAdmin):
    '''
    Custom class to override default admin method
    '''
    def get_queryset(self, request):
        '''
        custom queryset method to override default admin method
        '''
        qs = AppUser.all_objects.all()
        return qs

admin.site.register(AppUser, AppUserAdmin)
admin.site.register(BlackListedToken)
