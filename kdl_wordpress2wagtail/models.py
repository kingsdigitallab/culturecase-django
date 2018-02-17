from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class KDLWordpressReference(models.Model):
    '''
    Records a connection between a Wordpress object and a Wagtail object
    '''
    wordpressid = models.CharField(max_length=32, blank=False, null=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    tags = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return '{}->{}:{}'.format(
            self.wordpressid,
            self.content_type,
            self.object_id
        )
