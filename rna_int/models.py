from django.db import models

# Create your models here.


class Entities(models.Model):
    species = models.CharField(max_length=50, null=True)
    entity_type = models.CharField(max_length=50, null=True)
    name = models.CharField(max_length=100, null=True)


class Mirna(models.Model):
    species = models.CharField(max_length=50, null=True)
    pre_mirna = models.CharField(max_length=100, null=True)
    mature_mirna = models.CharField(max_length=100, null=True)
    pre_mirna_mirbase_entry = models.CharField(max_length=50)
    mature_mirna_mirbase_entry = models.CharField(max_length=50)
    cell_line = models.CharField(max_length=100)
    family = models.CharField(max_length=50)
    cluster = models.CharField(max_length=200)
    reproductive_process = models.CharField(max_length=200)
    reference = models.CharField(max_length=100)


class MirnaEntity(models.Model):
    mirna_id = models.IntegerField()
    pre_mirna = models.CharField(max_length=100, null=True)
    mature_mirna = models.CharField(max_length=100, null=True)
    entity_id = models.IntegerField()
    entity_type = models.CharField(max_length=50, null=True)
    entity_name = models.CharField(max_length=100, null=True)
    database = models.CharField(max_length=50, null=True)
    occurrence = models.IntegerField(null=True)
    info = models.CharField(max_length=500, null=True)
