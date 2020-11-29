from django.shortcuts import render
from .forms import TextForm
# Create your views here.
import pandas as pd
import json

data_file = '/home/cidmirna/cidmirnaweb/crc_finder/all_genes_CRCs.csv'

data_file2 = '/home/cidmirna/cidmirnaweb/crc_finder/predicted_CRCs.csv'
# print(data_df)

def CRC_search(gene_names, all_motifs, data_df):

    print(gene_names)
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

def get_crc(request):

    if request.method == 'POST':
        form = TextForm(request.POST)
        if form.is_valid():
            motif_data = form.cleaned_data['motif_search']
            gene_data = form.cleaned_data['gene_search']

            gene_names = gene_data.lower().split(',')
            all_gene_names = [motif.strip(' ') for motif in gene_names]
            all_motifs = motif_data.lower().split(',')
            all_motifs = [motif.strip(' ') for motif in all_motifs]
            # print('Gene', gene_name)
            # print('Motifs', all_motifs)
            data_df = pd.read_csv(data_file)
            result_df = CRC_search(all_gene_names, all_motifs, data_df)
            result_records = result_df[['gene_name', 'cluster_motifs']].reset_index(drop = True).to_json(orient = 'records')

            result_records = json.loads(result_records)

            # print(result_records)

            full_data = {'gene' : gene_data, 'motif': motif_data, 'result': result_records}

            form = TextForm()
            return render(request, 'crc_webpage.html', {'full_data': full_data,'data':form,})

    form = TextForm()
    # inp_value = request.GET.get('results', 'This is a default value')

    # response = {'inp_value': inp_value}
    return render(request, 'crc_webpage.html', {'data': form})

def home(request):
    return render(request,'crc.html')

def get_novel_crc(request):

    if request.method == 'POST':
        form = TextForm(request.POST)
        if form.is_valid():
            motif_data = form.cleaned_data['motif_search']
            gene_data = form.cleaned_data['gene_search']

            gene_names = gene_data.lower().split(',')
            all_gene_names = [motif.strip(' ') for motif in gene_names]
            all_motifs = motif_data.lower().split(',')
            all_motifs = [motif.strip(' ') for motif in all_motifs]
            # print('Gene', gene_name)
            # print('Motifs', all_motifs)
            data_df2 = pd.read_csv(data_file2)
            result_df = CRC_search(all_gene_names, all_motifs, data_df2)
            result_df = result_df.round({"CRC_score":2})
            result_records = result_df[['gene_name', 'cluster_motifs', 'CRC_score']].reset_index(drop = True).to_json(orient = 'records')
            result_records = json.loads(result_records)

            # print(result_records)

            full_data = {'gene' : gene_data, 'motif': motif_data, 'result': result_records}

            form = TextForm()
            return render(request, 'novel_crcs.html', {'full_data': full_data,'data':form,})

    form = TextForm()
    # inp_value = request.GET.get('results', 'This is a default value')

    # response = {'inp_value': inp_value}
    return render(request, 'novel_crcs.html', {'data': form})

