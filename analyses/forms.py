import logging

from django import forms
from django.core.validators import validate_email
from django.forms import CharField, Textarea, ValidationError, ModelForm, IntegerField

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.bootstrap import AppendedText

from analyses.models import Analysis as AnalysisModel


class Analysis(ModelForm):
    file = forms.FileField(required=True, label="Sequencing data (FASTA or FASTQ)")

    class Meta:
        model = AnalysisModel
        fields = ('file', 'email', 'organism')

    def __init__(self, *args, **kwargs):
        super(Analysis, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'

        self.helper.add_input(Submit('submit', 'Analyse', css_class='btn btn-primary offset4'))