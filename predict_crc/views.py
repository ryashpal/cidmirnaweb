from django.shortcuts import render
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from predict_crc.helper_functions import *

import pandas as pd
import json
import os
from random import randint

temp_csv_folder = './crc_finder_pipeline/temp_csv_files/'

def random_filename():
    letters = 'abcdefghijklmnopqrstuvwxyz'
    filename_len = randint(3,10)
    filename = temp_csv_folder
    for ix in range(filename_len):
        index = randint(0,25)
        filename = filename + letters[index]
    filename = filename + '.csv'
    return filename

def run_pipeline(input_file):

    print('Loading input file - ', input_file )
    data_df = generate_combinatorial_pairs(input_file)
    print('Combinatorial motif pairs generated - ', len(data_df) )
    data_df = extract_features(data_df)
    print('Features extracted...')
    data_df_scaled = feature_transformation(data_df.copy())
    print('Features scaled for predictions...')
    predictions_df = predict_pairs(data_df_scaled, data_df)
    print('Predictions performed...')
    csvDownload_filename = random_filename()
    output_filepath = csvDownload_filename.split('/')[-1]
    putative_CRC = generate_crc(predictions_df, output_filepath)
    print('Output bed file generated - ', output_filepath)

    return output_filepath, putative_CRC



def file_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        uploaded_file_url = '.' + uploaded_file_url
        print(uploaded_file_url)

        # Running pipeline
        output_filepath, result_df = run_pipeline(uploaded_file_url)
        os.remove(uploaded_file_url)

        result_records = result_df[['gene_name', 'cluster_motifs', 'CRC_score']].reset_index(drop = True).to_json(orient = 'records')
        result_records = json.loads(result_records)


        return render(request, 'predict_crc.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'predict_crc.html')

