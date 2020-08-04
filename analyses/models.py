from django.db import models

class Analysis(models.Model):
    """
    Basic model for keeping track of analyses submitted
    """

    email = models.EmailField(max_length=254, blank=False)
    organism = models.CharField(max_length=250, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    analysed = models.BooleanField(default=False)
    sent = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'analyses'

    def __unicode__(self):
        return u'Analysis %s for %s' % (self.pk, self.email)


class Filename(models.Model):
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    filename = models.TextField(blank=True)
    input = models.BooleanField(default=True)

    def __unicode__(self):
        return u'%s for analysis %s (%s)' % (self.filename, self.analysis, 'input' if self.input else 'output')

class Job(models.Model):
    """
    An attempt at analysing the data
    """
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    command_line = models.TextField()
    machine = models.TextField()
    process = models.TextField(blank=True, null=True)
    exit_code = models.IntegerField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return u'Job for %s' % self.analysis