from django import forms

class Linc2functionForm(forms.Form):
    fasta = forms.CharField(widget=forms.Textarea, label='', required=True)

