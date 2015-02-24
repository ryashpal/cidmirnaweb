import logging

from django.shortcuts import render, render_to_response

from analyses.views import home


def about(request):
    return render(request, 'about.html')