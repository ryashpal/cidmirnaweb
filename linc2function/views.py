from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render
from .forms import Linc2functionForm
from .linc2functionUsecase import annotateFastaString as annotateFastaString
from .linc2functionUsecase import annotateFastaFile as annotateFastaFile
# Create your views here.

import logging

def linc2function(request):
    if request.method == 'POST':
        form = Linc2functionForm(request.POST)
        if form.is_valid():
            fasta = form.cleaned_data['fasta']
            model = request.POST['modelRadios']
            modelType = request.POST['typeRadios']
            args = annotateFastaString(fasta, model, modelType)
            return render(request, 'linc2function_result.html', args)
    elif request.method == 'GET':
        uid = request.GET.get('uid', '')
        model = request.GET.get('model', '')
        modelType = request.GET.get('type', '')
        if uid and model:
            args= annotateFastaFile(uid, model, modelType)
            return render(request, 'linc2function_result.html', args)
    form = Linc2functionForm()
    return render(request, 'linc2function.html', {'form': form})


def datasource_comparison(request):
    return render(request, 'compare.html')


def linc2function_data_selection(request):
    return render(request, 'linc2function_data_selection.html')


def linc2function_feature_tree(request):
    return render(request, 'linc2function_feature_tree.html')

