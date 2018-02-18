'''
Created on 15 Feb 2018

@author: Geoffroy Noel
'''

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class KDLWordpressReference(models.Model):
    '''
    Wordpress object registry inside Django.
    Records a connection between a Wordpress object and a Django object.
    '''
    wordpressid = models.CharField(
        max_length=32, blank=False, null=False, unique=True
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    django_object = GenericForeignKey('content_type', 'object_id')
    # If True the django_object should never be deleted by the import
    # e.g. Wagtail page root, it pre-exists the import, we leave it there.
    # Note that the actual reference instance can be deleted.
    protected = models.BooleanField(default=False, null=False, blank=False)

    def __str__(self):
        return '{}->{}:{}'.format(
            self.wordpressid,
            self.content_type,
            self.object_id
        )

    @classmethod
    def get_django_object(cls, wordpressid):
        ret = None

        reference = cls.objects.filter(
            wordpressid=wordpressid
        ).first()

        if reference:
            ret = reference.django_object

            if not ret:
                # Special case: delete this ghost reference
                # it points to a django record which has been deleted from DB
                # but that wasn't caught by the on_delete for some reason
                # (e.g. bulk delete or other method not triggering signals)
                #
                # We have to delete it otherwise client might think it doesn't
                # exist and generate error by trying to create a new ref with
                # same wordpressid
                reference.delete()

        return ret

    @classmethod
    def get(cls, wordpressid):
        # TODO: cache it so we don't run the same query all the time
        return cls.get_django_object(wordpressid)

    @classmethod
    def set(cls, wordpressid, django_object, protected=False):
        ret = cls.get_django_object(wordpressid)

        if ret:
            ret.django_object = django_object
            ret.protected = protected
        else:
            ret = cls(
                wordpressid=wordpressid,
                django_object=django_object,
                protected=protected
            )
        ret.save()

        return ret
