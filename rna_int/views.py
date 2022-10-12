from django.shortcuts import render

from django.http import HttpResponse

from django.core.paginator import Paginator

from .models import Mirna
from .models import Entities
from .models import MirnaEntity


def mirna_list(request):
    mirnaList = Mirna.objects.all()
    page_number = request.GET.get('page', 1)
    paginate_result = do_paginate(mirnaList, page_number)
    mirnaList = paginate_result[0]
    paginator = paginate_result[1]
    base_url = 'mirna_list?'
    return render(request, 'mirna_list.html',
                      {'mirna_list': mirnaList, 'paginator' : paginator, 'base_url': base_url})


def mirna_search(request):

    preMirna = request.POST.get('pre_mirna', '').strip()
    if len(preMirna) == 0:
        preMirna = request.GET.get('pre_mirna', '').strip()

    matureMirna = request.POST.get('mature_mirna', '').strip()
    if len(matureMirna) == 0:
        matureMirna = request.GET.get('mature_mirna', '').strip()

    mirnaList = Mirna.objects.filter(pre_mirna__contains=preMirna).filter(mature_mirna__contains=matureMirna)

    page_number = request.GET.get('page', 1)
    paginate_result = do_paginate(mirnaList, page_number)
    mirnaList = paginate_result[0]
    paginator = paginate_result[1]
    base_url = 'mirna_search?pre_mirna=' + preMirna + "&mature_mirna=" + matureMirna + "&"

    return render(request, 'mirna_list.html',
                      {
                        'mirna_list': mirnaList
                        , 'paginator' : paginator
                        , 'base_url': base_url
                        , 'search_pre_mirna': preMirna
                        , 'search_mature_mirna': matureMirna
                      }
                )


def entity_list(request):
    entityList = Entities.objects.all()
    page_number = request.GET.get('page', 1)
    paginate_result = do_paginate(entityList, page_number)
    entityList = paginate_result[0]
    paginator = paginate_result[1]
    base_url = 'entity_list?'
    return render(request, 'entity_list.html',
                      {'entity_list': entityList, 'paginator' : paginator, 'base_url': base_url})


def entity_search(request):

    entityType = request.POST.get('entity_type', '').strip()
    if len(entityType) == 0:
        entityType = request.GET.get('entity_type', '').strip()

    name = request.POST.get('name', '').strip()
    if len(name) == 0:
        name = request.GET.get('name', '').strip()

    entityList = Entities.objects.filter(entity_type__contains=entityType).filter(name__contains=name)

    page_number = request.GET.get('page', 1)
    paginate_result = do_paginate(entityList, page_number)
    entityList = paginate_result[0]
    paginator = paginate_result[1]
    base_url = 'entity_search?entity_type=' + entityType + "&name=" + name + "&"

    return render(request, 'entity_list.html',
                      {
                        'entity_list': entityList
                        , 'paginator' : paginator
                        , 'base_url': base_url
                        , 'search_entity_type': entityType
                        , 'search_name': name
                      }
                )


def mirna_entity_list(request):
    mirnaEntityList = MirnaEntity.objects.all()
    page_number = request.GET.get('page', 1)
    paginate_result = do_paginate(mirnaEntityList, page_number)
    mirnaEntityList = paginate_result[0]
    paginator = paginate_result[1]
    base_url = 'mirna_entity_list?'
    return render(request, 'mirna_entity_list.html',
                      {'mirna_entity_list': mirnaEntityList, 'paginator' : paginator, 'base_url': base_url})


def mirna_entity_search(request):

    preMirna = request.POST.get('pre_mirna', '').strip()
    if len(preMirna) == 0:
        preMirna = request.GET.get('pre_mirna', '').strip()

    matureMirna = request.POST.get('mature_mirna', '').strip()
    if len(matureMirna) == 0:
        matureMirna = request.GET.get('mature_mirna', '').strip()

    entityType = request.POST.get('entity_type', '').strip()
    if len(entityType) == 0:
        entityType = request.GET.get('entity_type', '').strip()

    entityName = request.POST.get('entity_name', '').strip()
    if len(entityName) == 0:
        entityName = request.GET.get('entity_name', '').strip()

    database = request.POST.get('database', '').strip()
    if len(database) == 0:
        database = request.GET.get('database', '').strip()

    mirnaEntityList = MirnaEntity.objects.filter(pre_mirna__contains=preMirna).filter(mature_mirna__contains=matureMirna).filter(entity_type__contains=entityType).filter(entity_name__contains=entityName).filter(database__contains=database)

    page_number = request.GET.get('page', 1)
    paginate_result = do_paginate(mirnaEntityList, page_number)
    mirnaEntityList = paginate_result[0]
    paginator = paginate_result[1]
    base_url = 'mirna_entity_search?pre_mirna=' + preMirna + '&mature_mirna=' + matureMirna + '&entity_type=' + entityType + '&entity_name=' + entityName + '&database=' + database + '&'

    return render(request, 'mirna_entity_list.html',
                      {
                        'mirna_entity_list': mirnaEntityList
                        , 'paginator' : paginator
                        , 'base_url': base_url
                        , 'search_pre_mirna': preMirna
                        , 'search_mature_mirna': matureMirna
                        , 'search_entity_type': entityType
                        , 'search_entity_name': entityName
                        , 'search_database': database
                      }
                )


def do_paginate(data_list, page_number):

    ret_data_list = data_list
    # suppose we display at most 2 records in each page.
    result_per_page = 5
    # build the paginator object.
    paginator = Paginator(data_list, result_per_page)
    try:
        # get data list for the specified page_number.
        ret_data_list = paginator.page(page_number)
    except EmptyPage:
        # get the lat page data if the page_number is bigger than last page number.
        ret_data_list = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        # if the page_number is not an integer then return the first page data.
        ret_data_list = paginator.page(1)

    return [ret_data_list, paginator]
