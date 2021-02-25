import os
import subprocess
from django.conf import settings
import logging
from subprocess import Popen

def predict(fasta_id, uid):
    venvPath = os.path.join(settings.SPOTRNA_ROOT, '.venv/bin/python')
    spotrnaPath = os.path.join(settings.SPOTRNA_ROOT, 'SPOT-RNA-FRAGMENTED.py')
    outputPath = os.path.join(settings.BASE_DIR, 'static', 'tmp', uid)
    inputPath = os.path.join(outputPath, uid + '.fasta')
    ctFilePath = os.path.join(outputPath, fasta_id + '.ct')
    radiateImagePath = os.path.join(outputPath, fasta_id + '_radiate.png')
    lineImagePath = os.path.join(outputPath, fasta_id + '_line.png')
    try:
        if not os.path.isfile(ctFilePath):
            p = subprocess.Popen([venvPath, spotrnaPath, '--inputs', inputPath, '--outputs', outputPath], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
        if not os.path.isfile(radiateImagePath):
            subprocess.Popen(["java", "-cp", settings.SPOTRNA_ROOT + "/utils/VARNAv3-93.jar", "fr.orsay.lri.varna.applications.VARNAcmd", '-i', ctFilePath, '-o', radiateImagePath, '-algorithm', 'radiate', '-resolution', '8.0', '-bpStyle', 'lw'], stderr=subprocess.STDOUT, stdout=subprocess.PIPE, cwd=settings.SPOTRNA_ROOT).communicate()
        if not os.path.isfile(lineImagePath):
            subprocess.Popen(["java", "-cp", settings.SPOTRNA_ROOT + "/utils/VARNAv3-93.jar", "fr.orsay.lri.varna.applications.VARNAcmd", '-i', ctFilePath, '-o', lineImagePath, '-algorithm', 'line', '-resolution', '8.0', '-bpStyle', 'lw'], stderr=subprocess.STDOUT, stdout=subprocess.PIPE, cwd=settings.SPOTRNA_ROOT).communicate()
    except Exception as e:
        logging.error(e)
    return os.path.basename(radiateImagePath), os.path.basename(lineImagePath)

