from django.db import models

class Analysis(models.Model):
    """
    Basic model for keeping track of analyses submitted
    """

    email = models.EmailField(max_length=254, blank=False)
    organism = models.CharField(max_length=250, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    analysed = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)

    def __unicode__(self):
        return u'Analysis %s for %s' % (self.pk, self.email)


class Filename(models.Model):
    analysis = models.ForeignKey(Analysis)
    filename = models.TextField(blank=True)

    