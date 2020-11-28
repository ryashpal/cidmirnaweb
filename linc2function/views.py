import os
import random
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render

from .calculateCodingPotentialUsecase import calculate as calculateCodingPotential
from .predictSecondaryStructureUsecase import predict as predictSecondaryStructure
from .predictBindingSitesUsecase import predict as predictBindingSites
from .forms import Linc2functionForm
# Create your views here.

def linc2function(request):
    if request.method == 'POST':
        form = Linc2functionForm(request.POST)
        if form.is_valid():
            sequence = form.cleaned_data['sequence']
            model = request.POST['modelRadios']
            percentage = calculateCodingPotential(sequence, model)
            radiateImageName, lineImageName = predictSecondaryStructure(sequence)
            arc_diagram_path = os.path.join('tmp/', radiateImageName.split('.')[0].split('_')[0], radiateImageName)
            twod_diagram_path = os.path.join('tmp/', lineImageName.split('.')[0].split('_')[0], lineImageName)
            headers, data = predictBindingSites(sequence)
            #rbp_interactome_table = '<table style="width:100%"><tr><th>Firstname</th><th>Lastname</th><th>Age</th></tr><tr><td>Jill</td><td>Smith</td><td>50</td></tr><tr><td>Eve</td><td>Jackson</td><td>94</td></tr></table>'
            args = {
                'percentage': percentage, 
                'sequence': sequence, 
                'model': model, 
                'arc_diagram_path': arc_diagram_path, 
                'twod_diagram_path': twod_diagram_path, 
                'headers': headers, 
                'data': data, 
                }
            return render(request, 'linc2function_result.html', args)
    else:
        form = Linc2functionForm()
    return render(request, 'linc2function.html', {'form': form})

