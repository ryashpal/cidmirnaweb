import os
import subprocess
from django.conf import settings
from subprocess import Popen

def calculate(sequence, model):
    venvPath = os.path.join(settings.LINC2FUNCTION_ROOT, '../.venv/bin/python')
    linc2functionPath = os.path.join(settings.LINC2FUNCTION_ROOT, 'main.py')
    modelRoot = os.path.join(settings.LINC2FUNCTION_ROOT, 'models')
    scalerRoot = os.path.join(settings.LINC2FUNCTION_ROOT, 'scalers')
    model_function = 'predict_hs_model' if model == 'hs' else 'predict_sa_model'
    command = [venvPath, linc2functionPath, model_function, sequence, modelRoot, scalerRoot]
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    lines = [line for line in iter(p.stdout.readline, b'')]
    codingPotential = round(float(lines[-1].decode("utf-8").strip()[2:-2]) * 100.0, 2)
    print('codingPotential before: ', codingPotential)
    codingPotential = round(100.0 - codingPotential, 2)
    print('codingPotential after: ', codingPotential)
    return codingPotential

