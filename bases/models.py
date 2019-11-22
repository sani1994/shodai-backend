from django.db import models
from userProfile.models import UserProfile
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core import signals
from django.db import utils

# Create your models here.

class BaseModel(models.Model):
    created_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, 
        on_delete=models.DO_NOTHING,
        verbose_name=_("Created By"),
        null=True,
        blank=True,
        related_name='created_%(app_label)s_%(class)s_set',
        db_index=True,
        help_text=_("User who created it"))
    modified_on = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(UserProfile,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Modified By"),
        related_name='modified_%(app_label)s_%(class)s_set',
        null=True,
        blank=True,
        db_index=True,
        help_text=_("User who last modified"))
    
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created_on = timezone.now()
            self.created_by = self.pk
        self.modified = timezone.now()
        return super(BaseModel, self).save(*args, **kwargs)

    class Meta: 
        abstract = True