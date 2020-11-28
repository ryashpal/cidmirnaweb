from django import forms

class Linc2functionForm(forms.Form):
    sequence = forms.CharField(widget=forms.Textarea, label='', required=True)

