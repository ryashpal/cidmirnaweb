from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import TextForm
from django.http import HttpResponse

# Create your views here.
import pandas as pd
import json
from random import randint

data_file = '/home/cidmirna/cidmirnaweb/crc_finder/all_genes_CRCs.csv'
data_file2 = '/home/cidmirna/cidmirnaweb/crc_finder/predicted_CRCs.csv'
temp_csv_folder = '/home/cidmirna/cidmirnaweb/crc_finder/temp_csv_files'

# data_file = './all_genes_CRCs.csv'
# data_file2 = './predicted_CRCs.csv'
# temp_csv_folder = './crc_finder_app/temp_csv_files/'
# print(data_df)

data_df = pd.read_csv(data_file)
data_df2 = pd.read_csv(data_file2)


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
    filename = temp_csv_folder
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

            if motif_data == 'undefined':
                motif_data = ''
                gene_data = ''
                crc_cutoff = '0.8'
            
            if crc_cutoff == None or crc_cutoff == '':
                crc_cutoff = 0.8

            gene_names = gene_data.lower().split(',')
            all_gene_names = [motif.strip(' ') for motif in gene_names]
            all_motifs = motif_data.lower().split(',')
            all_motifs = [motif.strip(' ') for motif in all_motifs]
            print('CUT-OFF', type(crc_cutoff))
            # print('Motifs', all_motifs)
            result_df = CRC_search(all_gene_names, all_motifs, data_df)
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

def get_novel_crc(request):

    if request.method == 'GET':
        form = TextForm(request.GET)
        if form.is_valid():
            motif_data = form.cleaned_data['motif_search']
            gene_data = form.cleaned_data['gene_search']
            crc_cutoff = form.cleaned_data['cut_off']

            if motif_data == 'undefined':
                motif_data = ''
                gene_data = ''
                crc_cutoff = '0.8'
            # page = form.cleaned_data['page_number']

            if crc_cutoff == '':
                crc_cutoff = 0.8

            gene_names = gene_data.lower().split(',')
            all_gene_names = [motif.strip(' ') for motif in gene_names]
            all_motifs = motif_data.lower().split(',')
            all_motifs = [motif.strip(' ') for motif in all_motifs]
            # print('Gene', gene_name)
            # print('Motifs', all_motifs)
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

            # Pagination
            
            page = request.GET.get('page', 1)
            # print(page)
            
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
            return render(request, 'novel_crcs.html', {'full_data': full_data,'data':form,'file_name' : filename})

    form = TextForm()
    # inp_value = request.GET.get('results', 'This is a default value')

    # response = {'inp_value': inp_value}
    return render(request, 'novel_crcs.html', {'data': form})

