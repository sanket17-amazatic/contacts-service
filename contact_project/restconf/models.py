'''
Base model implementing SoftDeletion of records for all models
And function for uploading profile image
'''
import os
from django.db import models
from django.contrib.auth.models import UserManager
from django.db.models.query import QuerySet
from django.utils import timezone

class SoftDeletionQuerySet(QuerySet):
    '''
    Used for returning object on query set
    '''
    def delete(self):
        '''
        Bulk deleting a queryset
        '''
        return super().update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def alive(self):
        '''
        Helper method for returning un-deleted objects
        '''
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        '''
        Helper method for returning deleted objects
        '''
        return self.exclude(deleted_at__isnull=True)

class SoftDeletionManager(models.Manager):
    '''
     Executed when objects/all_object is called on any model
    '''
    def __init__(self, *args, **kwargs):
        '''
        alive_only attribute is fetched and set
        '''
        self.alive_only = kwargs.pop('alive_only', True)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        '''
        Overrided default get_queryset()
        Returns filtered data whose deleted_at is None.
        Filtering is dependent on alive_only attribute 
        '''
        if self.alive_only:
            return SoftDeletionQuerySet(self.model).filter(deleted_at__isnull=True)
        return SoftDeletionQuerySet(self.model)

class ContactAppManager(UserManager, SoftDeletionManager):
    def __init__(self, *args, **kwargs):
        '''
        alive_only attribute is fetched and set
        '''
        self.alive_only = kwargs.pop('alive_only', True)
        super(SoftDeletionManager, self).__init__(*args, **kwargs)

class SoftDeletionModel(models.Model):
    '''
    All the models inheriting this class will have deleted_at attribute.
    While creating object it is set to null.
    '''
    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = ContactAppManager()
    all_objects = ContactAppManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self):
        '''
        This method is execute on calling .delete() method
        deleted_at attribute is set to current timestamp
        '''
        self.deleted_at = timezone.now()
        self.save()


