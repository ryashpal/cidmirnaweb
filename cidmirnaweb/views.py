import logging

from django.shortcuts import render, render_to_response


def about(request):
    return render(request, 'about.html')

def datasource_comparison(request):
    return render(request, 'compare.html')

