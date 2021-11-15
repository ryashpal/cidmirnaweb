from django import forms

class TextForm(forms.Form):
    gene_search = forms.CharField(label='Gene Search', max_length=100, required=False,
                                    widget=forms.TextInput(attrs={'placeholder': 'Eg: FTL, RP11-399B17.1'}))
    motif_search = forms.CharField(label='Motif Search', max_length=100, required=False,
                                    widget=forms.TextInput(attrs={'placeholder': 'Eg: GATA2, SOX6'}))
    cut_off = forms.CharField(label='Cut-off', max_length=50, required=False,
                                    widget=forms.TextInput(attrs={'placeholder': 'Eg: 0.5 to 1.0'}))

    PPI_CHOICES = [
    ('ppi', 'PPI known'),
    ('no_ppi', 'PPI unknown')
    ]

    MODEL_CHOICES = [
    ('cnn', 'CNN'),
    ('rfc', 'RFC')
    ]

    ppi = forms.ChoiceField(choices = PPI_CHOICES)
    model_choice = forms.ChoiceField(choices = MODEL_CHOICES)
    # cut_off = forms.IntegerField(widget=forms.NumberInput(attrs={'type':'range', 'step': 0.01, 'min': 0.5, 'max': 0.99, 'value' : 0.8, 'id':'cut_off_range'}), required=False)



    def __init__(self, *args, **kwargs):
        super(TextForm, self).__init__(*args, **kwargs)
        self.fields['gene_search'].widget.attrs.update({'style' : 'width:300px'})
        self.fields['motif_search'].widget.attrs.update({'style' : 'width:300px'})
        self.fields['cut_off'].widget.attrs.update({'style' : 'width:300px'})

