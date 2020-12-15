import os
import logging
import uuid
from django.conf import settings
from Bio import SeqIO

from .calculateCodingPotentialUsecase import calculate as calculateCodingPotential
from .calculateTriplexFormingPotentialUsecase import calculate as calculateTriplexFormingPotential
from .predictSecondaryStructureUsecase import predict as predictSecondaryStructure
from .predictRBPBindingSitesUsecase import predict as predictRBPBindingSites
from .predictRNABindingSitesUsecase import predict as predictRNABindingSites


def annotateFastaString(fasta, model, modelType):
    uid = str(uuid.uuid4())
    outputPath = os.path.join(settings.BASE_DIR, 'static', 'tmp', uid)
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
    fastaFilePath = os.path.join(outputPath, uid + '.fasta')
    with open(fastaFilePath, 'w') as fastaFile:
        fastaFile.write(fasta)
    return annotateFastaFile(uid, model, modelType)


def annotateFastaFile(uid, model, modelType):
    outputPath = os.path.join(settings.BASE_DIR, 'static', 'tmp', uid)
    fastaFilePath = os.path.join(outputPath, uid + '.fasta')
    sequence = ''
    fasta_id = ''
    for record in SeqIO.parse(fastaFilePath, "fasta"):
        if record:
            sequence = str(record.seq)
            fasta_id = record.id
            break

    args = {}
    if sequence and fasta_id:
        percentage = calculateCodingPotential(sequence, model, modelType)
        tfp = calculateTriplexFormingPotential(sequence)
        radiateImageName, lineImageName = predictSecondaryStructure(fasta_id, uid)
        arc_diagram_path = os.path.join('tmp', uid, lineImageName)
        twod_diagram_path = os.path.join('tmp', uid, radiateImageName)
        rbp_headers, rbp_data = predictRBPBindingSites(sequence)
        rna_headers, rna_data = predictRNABindingSites(fasta_id, uid)
        url = settings.EXTERNAL_BASE_URL + '/linc2function?uid=' + uid + '&model=' + model + '&type=' + modelType
        args = {
            'percentage': percentage, 
            'tfp': tfp, 
            'sequence': sequence, 
            'model': model, 
            'type': modelType, 
            'arc_diagram_path': arc_diagram_path, 
            'twod_diagram_path': twod_diagram_path, 
            'rbp_headers': rbp_headers, 
            'rbp_data': rbp_data, 
            'rna_headers': rna_headers, 
            'rna_data': rna_data, 
            'transcript_id': fasta_id, 
            'url': url, 
            }
        logging.info('linc2function|' + model + '|' + modelType + '|' + fasta_id + '|' + sequence + '|' + uid + '|' + str(percentage))

    return args

