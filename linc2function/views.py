import os
import random
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render
from Bio import SeqIO
from tempfile import NamedTemporaryFile


from .calculateCodingPotentialUsecase import calculate as calculateCodingPotential
from .predictSecondaryStructureUsecase import predict as predictSecondaryStructure
from .predictBindingSitesUsecase import predict as predictBindingSites
from .forms import Linc2functionForm
# Create your views here.

def linc2function(request):
    if request.method == 'POST':
        form = Linc2functionForm(request.POST)
        if form.is_valid():
            fasta = form.cleaned_data['fasta']
            fastaFile = NamedTemporaryFile(delete=False, suffix='.fasta')
            fastaFile.write(fasta.encode())
            fastaFile.close()

            sequence = ''
            fasta_id = 'N/A'
            for record in SeqIO.parse(fastaFile.name, "fasta"):
                if record:
                    sequence = str(record.seq)
                    fasta_id = record.id
                    break

            if sequence:
                model = request.POST['modelRadios']
                percentage = calculateCodingPotential(sequence, model)
                radiateImageName, lineImageName = predictSecondaryStructure(fastaFile)
                arc_diagram_path = os.path.join('tmp/', radiateImageName.split('.')[0].split('_')[0], radiateImageName)
                twod_diagram_path = os.path.join('tmp/', lineImageName.split('.')[0].split('_')[0], lineImageName)
                headers, data = predictBindingSites(sequence)
                args = {
                    'percentage': percentage, 
                    'sequence': sequence, 
                    'model': model, 
                    'arc_diagram_path': arc_diagram_path, 
                    'twod_diagram_path': twod_diagram_path, 
                    'headers': headers, 
                    'data': data, 
                    'transcript_id': fasta_id, 
                    }
                os.unlink(fastaFile.name)
                return render(request, 'linc2function_result.html', args)
            os.unlink(fastaFile.name)
    form = Linc2functionForm()
    return render(request, 'linc2function.html', {'form': form})

