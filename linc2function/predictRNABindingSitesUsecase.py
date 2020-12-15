import os
import subprocess
from subprocess import Popen
from django.conf import settings

def predict(fasta_id, uid):
    riblastPath = os.path.join(settings.RIBLAST_ROOT, 'RIblast')
    ris = 'ris'
    inputFlag = '-i'
    outputPath = os.path.join(settings.BASE_DIR, 'static', 'tmp', uid)
    inputPath = os.path.join(outputPath, uid + '.fasta')
    outputFlag = '-o'
    outputFile = os.path.join(outputPath, fasta_id + '.riblast')
    dbFlag = '-d'
    dbPath = os.path.join(settings.RIBLAST_ROOT, 'mirbase.db', 'mirbase.db')
    command = [riblastPath, ris, inputFlag, inputPath, outputFlag, outputFile, dbFlag, dbPath]
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    lines = [line for line in iter(p.stdout.readline, b'')]
    data = []
    headers = []
    last_line = lines[len(lines)-1].decode('utf-8').strip()
    if lines and last_line == 'RIblast ris mode has finished.':
        with open(outputFile) as outputFileHandle:
            outputLines = outputFileHandle.readlines()
            headers = outputLines[2].strip().split(',')[3:]
            for outputLine in outputLines[3:]:
                data.append(outputLine.strip().split(',')[3:])
    return headers, data

if __name__ == "__main__":
    print(predict('test_mrna', '60c72a38-4420-47a6-b866-bab6f91f2665'))
