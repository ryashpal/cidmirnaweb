from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import TextForm
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings

# Create your views here.
import pandas as pd
import json
import os
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
            csvDownload_filename = random_filename('csv')
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

#   csv_file = temp_csv_folder + csv_file
  csv_file = '/Users/tarunbonu/Tarun/sem_4/minor_thesis/crc_finder_final/predicted_CRCs.csv'
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

def random_filename(type):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    filename_len = randint(3,10)
    filename = temp_csv_folder
    for ix in range(filename_len):
        index = randint(0,25)
        filename = filename + letters[index]
    if type == 'csv':
        filename = filename + '.csv'
    else:
        filename = filename + '.bed'
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

def file_sanity_check(bed_file):

    with open(bed_file, 'r') as fp:
        all_lines = fp.readlines()

    for line in all_lines:
        line = line.strip('\n')
        elements = line.split('\t')
        if len(elements) != 6:
            print('1')
            return 0
        
        if not elements[0].startswith('chr'):
            print('2')
            return 0

        try:
            elements[1] = int(elements[1])
            elements[2] = int(elements[2])
            elements[4] = int(elements[4])
        except:
            return 0

        if not elements[5] in ['+', '-']:
            print('5', elements[5])
            return 0

    return 1


def file_upload(request):
    if request.method == 'POST':
        try:
            if request.FILES['myfile']:
                myfile = request.FILES['myfile']
                fs = FileSystemStorage()
                filename = fs.save(myfile.name, myfile)
                src_filename = settings.BASE_DIR + fs.url(filename)
                uploaded_file_url = settings.BASE_DIR + settings.TEMP_CSV_FILE.replace('.', '') + myfile.name
                
                os.rename(src_filename, uploaded_file_url)
                print(uploaded_file_url)
        except:
            print('In exception now')
            bedtext = request.POST.get("bedtext")
            uploaded_file_url = settings.BASE_DIR + random_filename('bed')
            uploaded_file_url = uploaded_file_url.replace('./', '/')
            with open(uploaded_file_url, 'w') as fp:
                fp.writelines(bedtext)
            print(uploaded_file_url)
        

    if not request.method == 'GET':
        if not file_sanity_check(uploaded_file_url):
            print('Reject this file. Invalid file format')
            return render(request, 'crc_finder.html', {'reject' : 'reject'})

        # Running pipeline
        # output_filepath, result_df = run_pipeline(uploaded_file_url)

        output_file_csv = settings.BASE_DIR + random_filename('csv')
        output_file_csv = output_file_csv.replace('./', '/')
        output_file_bed = output_file_csv.replace('.csv', '.bed')

        python_call = 'python3 /Users/tarunbonu/Tarun/sem_4/minor_thesis/crc_finder_final/crc_finder.py -m ' + \
            uploaded_file_url + \
            ' -b ' + output_file_bed + ' -c ' + output_file_csv
        
        print('Running pipeline..')
        print(python_call)
        os.system(python_call)
        os.remove(uploaded_file_url)
        result_df = pd.read_csv(output_file_csv)
        filename = output_file_csv.split('/')[-1]

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

    import os, tempfile, zipfile
    from wsgiref.util import FileWrapper
    from django.conf import settings
    import mimetypes
    
    csv_file = settings.TEMP_CSV_FILE + csv_file
    print('Downloading file.. ', csv_file)
    wrapper      = FileWrapper(open(csv_file))
    content_type = mimetypes.guess_type(csv_file)[0]
    response     = HttpResponse(wrapper,content_type=content_type)
    response['Content-Length']      = os.path.getsize(csv_file)    
    if csv_file.endswith('.csv'):
        response['Content-Disposition'] = 'attachment; filename=%s' % ("CRCs.csv")
    else:
        response['Content-Disposition'] = 'attachment; filename=%s' % ("CRCs.bed")
    # os.remove(csv_file)
    return response

