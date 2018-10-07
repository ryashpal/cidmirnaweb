from django.shortcuts import render

from bioinformatics.models import Page

def standard_page(request, page_name):
    page = Page.objects.get(internal_name=page_name)
    context = {
        'page' : page
    }
    return render(request, 'standardpage.html', context)
    

def generate_standard_view(name):
    def generic_page(request):
        return standard_page(request, name)
    return generic_page

home = generate_standard_view('home')
people = generate_standard_view('people')
research = generate_standard_view('research')
publications = generate_standard_view('publications')
training = generate_standard_view('training')
news = generate_standard_view('news')

