import os
import logging

from django.urls import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.conf import settings
from django.core.mail import mail_admins

from analyses.forms import Analysis as AnalysisForm
from analyses.models import Analysis, Filename


def save_file(request_file, filename):
    logging.info("Saving to %s" % filename)
    dir_name = os.path.dirname(filename)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    with open(filename, 'wb+') as destination:
        for chunk in request_file.chunks():
            destination.write(chunk)

def home(request):
    if request.POST:
        form = AnalysisForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            analysis_id = form.instance.id
            filename = os.path.basename(request.FILES['file'].name)

            mapping = Filename(analysis=form.instance, filename=filename)
            mapping.save()

            target_directory = os.path.join(settings.UPLOAD_DIRECTORY, str(analysis_id))
            target_filename = os.path.join(target_directory, 'uploaded')
            save_file(request.FILES['file'], target_filename)

            mail_admins("Someone submitted a file to CID-miRNA", "With ID: %s" % analysis_id)

            return HttpResponseRedirect(reverse('success'))

    else:
        form = AnalysisForm()

    return render(request, 'home.html', { 'form' : form })


def analysis_submitted(request):
    return render(request, 'submitted.html')
    