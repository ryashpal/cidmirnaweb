from django.shortcuts import render, redirect


def about(request):
    return render(request, 'about.html')


def datasource_comparison(request):
    return render(request, 'compare.html')


def download(request):
    fileName = request.GET.get('file_name')
    fileName = fileName.replace(' ', '+')
    return redirect('/media/gff3/' + fileName)
