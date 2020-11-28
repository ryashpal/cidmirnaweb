from django import forms

class TextForm(forms.Form):
    gene_search = forms.CharField(label='Gene Search', max_length=100, required=False,
                                    widget=forms.TextInput(attrs={'placeholder': 'Eg: FTL, RP11-399B17.1'}))
    motif_search = forms.CharField(label='Motif Search', max_length=100, required=False,
                                    widget=forms.TextInput(attrs={'placeholder': 'Eg: GATA2, SOX6'}))


    def __init__(self, *args, **kwargs):
        super(TextForm, self).__init__(*args, **kwargs)
        self.fields['gene_search'].widget.attrs.update({'style' : 'width:306px'})
        self.fields['motif_search'].widget.attrs.update({'style' : 'width:300px'})

