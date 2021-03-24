from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import TextForm
from django.http import HttpResponse
from django.conf import settings

# Create your views here.
import pandas as pd
import json
from random import randint

print('Settings : ', settings)

data_df = pd.read_csv(settings.DATA_FILE)
data_df2 = pd.read_csv(settings.DATA_FILE2)


def CRC_search(gene_names, all_motifs, data_df):

    # print(gene_names)
    if not gene_names[0]:
        temp_df = data_df.copy()
    else:
        temp_df = data_df[data_df['gene_name'].str.lower().isin(gene_names)]

    if not all_motifs[0]:
        return temp_df

    clusters = []
    for ix, row in temp_df.iterrows():
        cluster = row['cluster']
        cluster_motifs = row['cluster_motifs'].lower().split(', ')

        cnt = 0
        for motif in all_motifs:
            if motif in cluster_motifs:
                cnt += 1

        if cnt == len(all_motifs):
            clusters.append(cluster)

    # print(clusters)
    temp_df = temp_df[temp_df['cluster'].isin(clusters)]

    return temp_df


def random_filename():
    letters = 'abcdefghijklmnopqrstuvwxyz'
    filename_len = randint(3,10)
    filename = settings.TEMP_CSV_FILE
    for ix in range(filename_len):
        index = randint(0,25)
        filename = filename + letters[index]
    filename = filename + '.csv'
    return filename


def get_crc(request):

    if request.method == 'GET':
        form = TextForm(request.GET)
        if form.is_valid():
            motif_data = form.cleaned_data['motif_search']
            gene_data = form.cleaned_data['gene_search']
            crc_cutoff = form.cleaned_data['cut_off']
            ppi = form.cleaned_data['ppi']

            if motif_data == 'undefined':
                motif_data = ''
                gene_data = ''
                crc_cutoff = '0.8'
                ppi = 'ppi'
            
            if crc_cutoff == None or crc_cutoff == '':
                crc_cutoff = 0.8

            gene_names = gene_data.lower().split(',')
            all_gene_names = [motif.strip(' ') for motif in gene_names]
            all_motifs = motif_data.lower().split(',')
            all_motifs = [motif.strip(' ') for motif in all_motifs]
            print('CUT-OFF', type(crc_cutoff))
            # print('Motifs', all_motifs)
            if ppi == 'ppi':
                result_df = CRC_search(all_gene_names, all_motifs, data_df)
            elif ppi == 'no_ppi':
                result_df = CRC_search(all_gene_names, all_motifs, data_df2)

            result_df = result_df.round({"CRC_score":2})
            result_df = result_df[['gene_name','cluster_motifs','CRC_score']]
            result_df = result_df[result_df['CRC_score'] >= float(crc_cutoff)]
            result_df = result_df.sort_values(by='CRC_score', ascending=False)
            csvDownload_filename = random_filename()
            filename = csvDownload_filename.split('/')[-1]
            result_df.to_csv(csvDownload_filename, index = False)
            result_records = result_df[['gene_name', 'cluster_motifs', 'CRC_score']].reset_index(drop = True).to_json(orient = 'records')
            result_records = json.loads(result_records)
            #Pagination
            page = request.GET.get('page', 1)
            paginator = Paginator(result_records, 50)
            try:
                result_records = paginator.page(page)
            except PageNotAnInteger:
                result_records = paginator.page(1)
            except EmptyPage:
                result_records = paginator.page(paginator.num_pages)

            # print(result_records)

            full_data = {'gene' : gene_data, 'motif': motif_data, 'result': result_records, 'crc_cutoff': crc_cutoff}

            form = TextForm()
            return render(request, 'crc_webpage.html', {'full_data': full_data,'data':form, 'file_name' : filename})

    form = TextForm()
    # inp_value = request.GET.get('results', 'This is a default value')

    # response = {'inp_value': inp_value}
    return render(request, 'crc_webpage.html', {'data': form})


def send_file(request, csv_file):

  import os, tempfile, zipfile
  from wsgiref.util import FileWrapper
  from django.conf import settings
  import mimetypes

  csv_file = temp_csv_folder + csv_file
  download_name ="example.csv"
  wrapper      = FileWrapper(open(csv_file))
  content_type = mimetypes.guess_type(csv_file)[0]
  response     = HttpResponse(wrapper,content_type=content_type)
  response['Content-Length']      = os.path.getsize(csv_file)    
  response['Content-Disposition'] = 'attachment; filename=%s' % ("CRCs.csv")
  os.remove(csv_file)
  return response


def home(request):
    return render(request,'crc.html')


from django.shortcuts import render
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
# from predict_crc.helper_functions import *

import pandas as pd
import json
import os
from random import randint

temp_csv_folder = settings.TEMP_CSV_FILE

def random_filename():
    letters = 'abcdefghijklmnopqrstuvwxyz'
    filename_len = randint(3,10)
    filename = temp_csv_folder
    for ix in range(filename_len):
        index = randint(0,25)
        filename = filename + letters[index]
    filename = filename + '.csv'
    return filename

# def run_pipeline(input_file):

#     print('Loading input file - ', input_file )
#     data_df = generate_combinatorial_pairs(input_file)
#     print('Combinatorial motif pairs generated - ', len(data_df) )
#     data_df = extract_features(data_df)
#     print('Features extracted...')
#     data_df_scaled = feature_transformation(data_df.copy())
#     print('Features scaled for predictions...')
#     predictions_df = predict_pairs(data_df_scaled, data_df)
#     print('Predictions performed...')
#     csvDownload_filename = random_filename()
#     output_filepath = csvDownload_filename.split('/')[-1]
#     putative_CRC = generate_crc(predictions_df, output_filepath)
#     print('Output bed file generated - ', output_filepath)

#     return output_filepath, putative_CRC


def file_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        uploaded_file_url = '.' + uploaded_file_url
        print(uploaded_file_url)

        # Running pipeline
        # output_filepath, result_df = run_pipeline(uploaded_file_url)
        os.remove(uploaded_file_url)
        result_df = pd.read_csv('./predict_crc/predicted_CRCs.csv')
        filename = 'predicted_CRCs.csv'

        result_records = result_df[['gene_name', 'cluster_motifs', 'CRC_score']].reset_index(drop = True).to_json(orient = 'records')
        result_records = json.loads(result_records)

        # page = request.GET.get('page', 1)
        # paginator = Paginator(result_records, 50)
        # try:
        #     result_records = paginator.page(page)
        # except PageNotAnInteger:
        #     result_records = paginator.page(1)
        # except EmptyPage:
        #     result_records = paginator.page(paginator.num_pages)

        full_data = {'result': result_records}

        return render(request, 'crc_finder.html', {'full_data': full_data, 'file_name' : filename})


        # return render(request, 'predict_crc.html', {
        #     'uploaded_file_url': uploaded_file_url
        # })
    return render(request, 'crc_finder.html')


def send_file(request, csv_file):

    print('HIIII')
    import os, tempfile, zipfile
    from wsgiref.util import FileWrapper
    from django.conf import settings
    import mimetypes

    csv_file = './predict_crc/' + csv_file
    print(csv_file)
    download_name = "example.csv"
    wrapper      = FileWrapper(open(csv_file))
    content_type = mimetypes.guess_type(csv_file)[0]
    response     = HttpResponse(wrapper,content_type=content_type)
    response['Content-Length']      = os.path.getsize(csv_file)    
    response['Content-Disposition'] = 'attachment; filename=%s' % ("CRCs.csv")
    # os.remove(csv_file)
    return response


# def get_novel_crc(request):

#     if request.method == 'GET':
#         form = TextForm(request.GET)
#         if form.is_valid():
#             motif_data = form.cleaned_data['motif_search']
#             gene_data = form.cleaned_data['gene_search']
#             crc_cutoff = form.cleaned_data['cut_off']

#             if motif_data == 'undefined':
#                 motif_data = ''
#                 gene_data = ''
#                 crc_cutoff = '0.8'
#             # page = form.cleaned_data['page_number']

#             if crc_cutoff == '':
#                 crc_cutoff = 0.8

#             gene_names = gene_data.lower().split(',')
#             all_gene_names = [motif.strip(' ') for motif in gene_names]
#             all_motifs = motif_data.lower().split(',')
#             all_motifs = [motif.strip(' ') for motif in all_motifs]
#             # print('Gene', gene_name)
#             # print('Motifs', all_motifs)
#             result_df = CRC_search(all_gene_names, all_motifs, data_df2)
#             result_df = result_df.round({"CRC_score":2})
#             result_df = result_df[['gene_name','cluster_motifs','CRC_score']]
#             result_df = result_df[result_df['CRC_score'] >= float(crc_cutoff)]
#             result_df = result_df.sort_values(by='CRC_score', ascending=False)
#             csvDownload_filename = random_filename()
#             filename = csvDownload_filename.split('/')[-1]
#             result_df.to_csv(csvDownload_filename, index = False)
#             result_records = result_df[['gene_name', 'cluster_motifs', 'CRC_score']].reset_index(drop = True).to_json(orient = 'records')
#             result_records = json.loads(result_records)

#             # Pagination
            
#             page = request.GET.get('page', 1)
#             # print(page)
            
#             paginator = Paginator(result_records, 50)
#             try:
#                 result_records = paginator.page(page)
#             except PageNotAnInteger:
#                 result_records = paginator.page(1)
#             except EmptyPage:
#                 result_records = paginator.page(paginator.num_pages)

#             # print(result_records)

#             full_data = {'gene' : gene_data, 'motif': motif_data, 'result': result_records, 'crc_cutoff': crc_cutoff}

#             form = TextForm()
#             return render(request, 'novel_crcs.html', {'full_data': full_data,'data':form,'file_name' : filename})

#     form = TextForm()
#     # inp_value = request.GET.get('results', 'This is a default value')

#     # response = {'inp_value': inp_value}
#     return render(request, 'novel_crcs.html', {'data': form})
