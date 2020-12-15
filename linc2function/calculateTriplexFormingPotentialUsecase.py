import os
import subprocess
from django.conf import settings
from subprocess import Popen

def calculate(sequence):
    venvPath = os.path.join(settings.LINC2FUNCTION_ROOT, '../.venv/bin/python')
    tfpPath = os.path.join(settings.LINC2FUNCTION_ROOT, 'feature_extraction/TriplexFpp.py')
    command = [venvPath, tfpPath, sequence]
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    lines = [line for line in iter(p.stdout.readline, b'')]
    tfp = round(float(lines[-1].decode("utf-8")) * 100.0, 2)
    return tfp
