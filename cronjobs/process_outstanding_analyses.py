#!/usr/bin/env python
"""
Go through all the analyses we haven't done and try to do them.
Go through all the completed analyses not sent and send them
"""

import os, sys
import logging
import datetime, subprocess
import random

if __name__ == '__main__':
    # need to add grandparent directories to get top directory to be considered a package
    path = os.path.dirname(sys.argv[0])
    path = os.path.abspath(os.path.realpath(os.path.join(path, "..")))
    if path not in sys.path:
        sys.path.append(path)

    from utils import environment
    environment.setup_settings()

    del path

    import django
    django.setup()


from django.conf import settings
from django.core.mail import mail_admins, mail_managers

from analyses.models import Job, Analysis, Filename
from utils.remote import Remote

AllowedCharacters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

def check_on_running_jobs():
    from django.template import Context, loader
    from django.utils import timezone

    import pytz

    running_jobs = Job.objects.filter(exit_code__isnull=True, process_id__isnull=False)
    for job in running_jobs:
        machine = Remote.standard_machine(job.machine)
        if machine.process_running(job.process_id):
            # still running
            continue

        succeeded = False
        exit_code_filename = os.path.join(settings.ANALYSIS_CODE_ROOT, 'exitcodes', 'exit%s.txt' % job.process_id)
        try:
            exit_code_file = machine.sftp.open(exit_code_filename)
            content = exit_code_file.read()
            exit_code_file.close()
            if not content:
                logging.warn("Exit code file is empty for analysis of : %s" % job.analysis.pk)
            else:
                try:
                    first_line = content.splitlines()[0].strip()
                    exit_code = int(first_line)
                    if exit_code == 0:
                        succeeded = True
                    else:
                        logging.error("Job %s exited with code %s" % (job.analysis.pk, exit_code))
                except ValueError:
                    logging.error("Exit code file not a number for %s: %s" % (job.analysis.pk, first_line))
                    exit_code = -2
        except (IOError, OSError):
            # file not there. Assume it failed
            logging.error("No exit code file for job: %s" % job.analysis.pk)
            exit_code = -1

        job.exit_code = exit_code
        job.end_time = timezone.now()
        job.save()

        if succeeded:
            job.analysis.analysed = True
            job.analysis.save()

            # copy the results back here. Put them somewhere "random" for the client to get
            while True:
                output_directory = ''.join(random.choice(AllowedCharacters) for _ in range(15))
                full_directory = os.path.join(settings.DELIVERY_ROOT, output_directory)
                if not os.path.exists(full_directory):
                    os.makedirs(full_directory)
                    break

            client_data_directory = os.path.join(settings.ANALYSIS_CODE_ROOT, 'clientdata')
            try:
                structure_file = os.path.join(full_directory, 'structures.txt')
                machine.sftp.get(os.path.join(client_data_directory, 'uploaded%s.final.structures' % job.analysis.pk), structure_file)
            except IOError as error:
                logging.error("Couldn't copy structures for analysis %s to %s: %s" % (job.analysis.pk, structure_file, error))
                structure_url = 'Error creating'
            else:
                structures = Filename(analysis=job.analysis, filename=structure_file, input=False)
                structures.save()
                structure_url = "%s%s" % (settings.EXTERNAL_BASE_URL, os.path.join(settings.DELIVERY_URL, output_directory, 'structures.txt'))

            try:
                fasta_file = os.path.join(full_directory, 'mirna.fa')
                machine.sftp.get(os.path.join(client_data_directory, 'uploaded%s.final.fasta' % job.analysis.pk), fasta_file)
            except IOError as error:
                logging.error("Couldn't copy fasta for analysis %s to %s: %s" % (job.analysis.pk, fasta_file, error))
                fasta_url = 'Error creating'
            else:
                fasta = Filename(analysis=job.analysis, filename=fasta_file, input=False)
                fasta.save()
                fasta_url = "%s%s" % (settings.EXTERNAL_BASE_URL, os.path.join(settings.DELIVERY_URL, output_directory, 'mirna.fa'))

            context = {
                'analysis' : job.analysis,
                'structure_url' : structure_url,
                'fasta_url' : fasta_url
                }

            content = loader.render_to_string('analysisfinishedemail.html', context=context)

            mail_managers("CID-miRNA files are ready to be delivered", content)


def analyse_outstanding():
    import shlex
    for analysis in Analysis.objects.filter(analysed=False):
        # check if there are already enough jobs running
        if Job.objects.filter(exit_code__isnull=True).count() >= settings.MAX_SIMULTANEOUS_ANALYSIS:
            break


        already_running = False
        for job in analysis.job_set.all():
            # Don't run jobs that are already running and don't run jobs that have failed,
            # since they'll probably just keep on failing
            if job.exit_code is None or job.exit_code != 0:
                already_running = True
                break
        
        if already_running:
            continue


        # copy the file there
        source_file = os.path.join(settings.UPLOAD_DIRECTORY, "%s" % analysis.pk, "uploaded")
        client_data_directory = os.path.join(settings.ANALYSIS_CODE_ROOT, 'clientdata')        
        target_file = os.path.join(client_data_directory, 'uploaded%s' % analysis.pk)

        logging.info("Connecting for %s" % analysis)
        machine = Remote.standard_machine(settings.ANALYSIS_MACHINE)
        logging.info("Putting file for analysis %s" % analysis)
        try:
            machine.sftp.put(source_file, target_file)
        except IOError as error:
            logging.error("Couldn't copy %s to %s on %s: %s" % (source_file, target_file, machine.hostname, error))
            continue

        logging.info("File for analysis %s uploaded" % analysis)
        # start the process
        command_line = './runandrecordexitcode.sh -vvv -p --output-directory %s %s' % (client_data_directory, target_file)
        job = Job(analysis=analysis, machine=machine.hostname, command_line=command_line)
        full_command = """cd %(directory)s; nohup bash -lc %(command_line)s > /dev/null 2>&1 < /dev/null & echo $!"""  % {
            'directory' : settings.ANALYSIS_CODE_ROOT,
            'command_line' : shlex.quote(command_line)   
        }
        command = ['/usr/bin/ssh']
        if machine.port:
            command.extend(['-p', str(machine.port)])
        command.extend(['%s@%s' % (machine.username, machine.hostname), full_command])
        logging.info("Running: '%s' in '%s'" % (' '.join(command), machine.hostname))
        proc = subprocess.Popen(command, close_fds=True, stdout=subprocess.PIPE)
        job.process_id = int(proc.stdout.read())   #capture the remote PID
        job.save()


def main(args):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    # can't really think of what options I want for this yet
    parameters = parser.parse_args(args)

    check_on_running_jobs()
    analyse_outstanding()

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
