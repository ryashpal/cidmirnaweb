import keras
import joblib
import os
import pickle5 as pickle
import pandas as pd
from random import randint
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from functools import partial
from multiprocessing import Pool

gene_data_df = pd.read_csv('./predict_crc/data/gene_data.csv')
gene_data_df['chromosome'] = 'chr' + gene_data_df['chromosome']

protein_path = './predict_crc/data/9606.protein_links_names.csv'
protein_df = pd.read_csv(protein_path)

dbd_df = pd.read_csv('./predict_crc/data/Homo_sapiens_TF_binding_domain.txt', sep= '\t', usecols= ['Symbol', 'Family'])

shape_path = '/tsonika-data/crc_finder_data/'

def generate_combinatorial_pairs(input_file):

    with open(input_file, 'r') as fp:
        all_motifs = fp.readlines()


    motifs_df = pd.DataFrame(columns = ['motif', 'bs_seq', 'chromosome', 'bs_pos', 'strand'])
    for ix, motif_line in enumerate(all_motifs):
        line_parts = motif_line.strip('\n').split('\t')
        # print(line_parts)
        motifs_df.loc[ix] = [line_parts[-3].split('_')[0], line_parts[-3].split('_')[1], line_parts[0], line_parts[1], line_parts[-1]]
        # print(line_parts)

    # print(motifs_df)

    gene_names = []
    gene_distances = []
    gene_pos = []

    for ix,row in motifs_df.iterrows():

        chromosome = row['chromosome']
        start_pos = int(row['bs_pos'])
        strand = row['strand']

        # print(chromosome, start_pos, strand)
        temp_gene_df = gene_data_df[(gene_data_df['chromosome'] == chromosome) & (gene_data_df['strand'] == strand)]
        temp_gene_df = temp_gene_df.assign(distance = temp_gene_df['position_start'].astype(int) - start_pos)
        temp_gene_df = temp_gene_df[temp_gene_df['distance'] > 0]
        temp_gene_df['distance'] = temp_gene_df['distance'].astype(int)
        temp_gene_df = temp_gene_df.sort_values('distance').reset_index(drop = True)

        try:
            gene_names.append(temp_gene_df.loc[0,'gene_name'])
            gene_pos.append(temp_gene_df.loc[0, 'position_start'])
            gene_distances.append(temp_gene_df.loc[0,'distance'])
        except:
            gene_names.append(np.NaN)
            gene_pos.append(np.NaN)
            gene_distances.append(np.NaN)

    motifs_df['ng'] = gene_names
    motifs_df['gene_start_pos'] = gene_pos
    motifs_df['dng'] = gene_distances
    motifs_df = motifs_df.sort_values('bs_pos').reset_index(drop = True)

    all_genes = set(motifs_df['ng'].to_list())

    data_df = pd.DataFrame(columns = ['motif1', 'bs1_seq', 'bs1_start_pos' ,
                                      'motif2', 'bs2_seq', 'bs2_start_pos',
                                      'dbbs', 'chromosome', 'strand', 'dng', 'ng', 'gene_start_pos'])

    for gene in all_genes:
        # print(gene)
        temp_motif = motifs_df[motifs_df['ng'] == gene]
        # print(temp_motif)

        for ix, row1 in temp_motif.iterrows():
            motif1 = row1['motif']
            motif1_pos = row1['bs_pos']
            for jx, row2 in temp_motif.iterrows():
                motif2 = row2['motif']
                motif2_pos = row2['bs_pos']
                if motif1 != motif2 and motif1_pos < motif2_pos:

                    data = [{'motif1':motif1,'bs1_seq':row1['bs_seq'],'bs1_start_pos':row1['bs_pos'],
                    'motif2':motif2,'bs2_seq':row2['bs_seq'],'bs2_start_pos':row2['bs_pos'],
                    'dbbs':int(row2['bs_pos']) - int(row1['bs_pos']),'chromosome':row1['chromosome'] , 'strand':row1['strand'],
                    'dng':row1['dng'], 'ng':row1['ng'], 'gene_start_pos': row1['gene_start_pos']}]
                    # print(data)
                    data_df = data_df.append(data, ignore_index=False)

    # print(data_df)
    data_df = data_df[data_df['dbbs'] <= 30]
    return data_df

def get_skew_score(bs_seq):

    bs_seq = bs_seq.lower()
    a_count = bs_seq.count('a')
    g_count = bs_seq.count('g')
    c_count = bs_seq.count('c')
    t_count = bs_seq.count('t')

    if ((g_count+c_count) == 0 or (a_count+t_count) == 0):
        return((g_count-c_count)/(g_count+c_count + 1), (a_count-t_count)/(a_count+t_count + 1))
    else:
        return((g_count-c_count)/(g_count+c_count), (a_count-t_count)/(a_count+t_count))


def generate_unique_positions(data_df): # For shape scoring

    all_positions = list()

    for ix, row in data_df.iterrows():

        bs1 = row['motif1'] + '_' + row['bs1_seq']
        position_1 = row['bs1_start_pos']
        chromosome = row['chromosome']

        bs2 = row['motif2'] + '_' + row['bs2_seq']
        position_2 = row['bs2_start_pos']

        all_positions.append(bs1 + '_' + chromosome + '_' +str(position_1))
        all_positions.append(bs2 + '_' + chromosome + '_' +str(position_2))

    all_positions = list(set(all_positions))

    return(all_positions)

def get_shape_score(all_motif_positions, shapes, all_indexes, ix):
    print('Threaded process with motif', ix+1)

    motif_line = all_motif_positions[ix]
    bs_details = motif_line.split('_')
    motif_len = len(bs_details[1])
    start_pos = int(bs_details[3]) + motif_len - 15
    chromosome = bs_details[2]

    # Calculate score
    with open('./calculated_shape_scores.txt', 'a') as fp:
        for shape in shapes:
            try:
                inner_indexer = all_indexes[shape + '_' + chromosome]
            except:
                score_line= str(ix) + '_' + motif_line + '_' + shape + '_' + str('NA') + '\n'
                fp.write(score_line)
                continue

            for file, positions in inner_indexer.items():
                file = file.replace('/home/tbon0008/lz25_scratch/tbon/deep_emscan/data/DNA_shapes/', shape_path)

                if positions[0] <= start_pos <= positions[1] - 30:
                    with open(file, 'rb') as handle:
                        inner_scores = pickle.load(handle)

                    # print(file)
                    scores = [inner_scores[pos] for pos in range(start_pos, start_pos + 31)]
                    final_score = round(sum(scores), 2)

                    score_line= str(ix) + '_' + motif_line + '_' + shape + '_' + str(final_score) + '\n'
                    # print(score_line)
                    fp.write(score_line)
                    del inner_scores
                elif positions[1] - 30 <= start_pos <= positions[1]:
                    with open(file, 'rb') as handle:
                        inner_scores = pickle.load(handle)

                    scores = [inner_scores[pos] for pos in range(start_pos, positions[1])]
                    final_score1 = round(sum(scores), 2)
                    last_pos = positions[1]
                    # print(file, positions[1] - start_pos)

                    inner_file_index = file.split('_')[-1].split('.')[0]
                    inner_file_index_1 = int(inner_file_index) + 1

                    split_file = file.split('_')
                    split_file[-1] = split_file[-1].replace(inner_file_index, str(inner_file_index_1))
                    file = '_'.join(split_file)
                    positions = inner_indexer[file]
                    # print(file, (30 - (last_pos - start_pos)))
                    with open(file, 'rb') as handle:
                        inner_scores = pickle.load(handle)

                    scores = [inner_scores[pos] for pos in range(positions[0], positions[0] + (30 - (last_pos - start_pos)))]
                    final_score2 = round(sum(scores), 2)

                    final_score = final_score1 + final_score2
                    # print(final_score1, final_score2, final_score)
                    score_line= str(ix) + '_' + motif_line + '_' + shape + '_' + str(final_score) + '\n'
                    # print(score_line)
                    fp.write(score_line)
                    del inner_scores

    return

def extract_shape_scores(all_motif_positions):

    chromosomes_considered = ['chr1', 'chr2', 'chr3', 'chr4', 'chr5', 'chr6', 'chr7', 'chrX',
           'chr8', 'chr9', 'chr11', 'chr10', 'chr12', 'chr13', 'chr14',
           'chr15', 'chr16', 'chr17', 'chr18', 'chr20', 'chr19', 'chrY',
           'chr22', 'chr21', 'chrM']
    #
    shapes = ['hg38.Rise', 'hg38.Roll', 'hg38.Shift', 'hg38.Slide', 'hg38.Tilt', 'hg38.Buckle', 'hg38.EP' , 'hg38.MGW', \
    'hg38.HelT' ,'hg38.OC2', 'hg38.Opening', 'hg38.ProT', 'hg38.Shear', 'hg38.Stagger', 'hg38.Stretch']

    all_indexes = {}

    print('Loading shape files')
    for shape in shapes:
        print(shape)
        for chromosome in chromosomes_considered:
        #     print(chromosome)

            shape_folder = shape_path + shape + '/' + shape + '.' + chromosome + '/'

            index_filename = shape_folder + shape + '.' + chromosome + '_INDEX.index'
            if index_filename.split('/')[-1] in ['hg38.OC2.chr22_INDEX.index', 'hg38.Opening.chr8_INDEX.index']:
                continue
        #     print(index_filename)

            with open(index_filename, 'rb') as handle:
                indexing = pickle.load(handle)

            all_indexes[shape + '_' +chromosome] = indexing

    all_scores = []
    positions_length = len(all_motif_positions)

    print('Calculation for', positions_length, 'positions')
    print('Parallelising Shape score calculation...')

    func_partial = partial(get_shape_score, all_motif_positions, shapes, all_indexes)

    with Pool(24) as p:
        p.map(func_partial, range(positions_length))

    print('Shape scores calculated...')

    del all_indexes
    return

def attach_shape_scores(data_df):

    with open('calculated_shape_scores.txt', 'r') as fp:
        all_scores = fp.readlines()
    os.remove('calculated_shape_scores.txt')

    bs_li = []
    chr_li = []
    bs_start_pos = []
    shape = []
    score = []

    shape_scores_df = pd.DataFrame(columns = ['bs', 'chr', 'start_pos', 'shape', 'score'])

    for ix, line in enumerate(all_scores):
        split_line = line.strip('\n').split('_')

        bs_li.append(split_line[1] + '_' + split_line[2])
        chr_li.append(split_line[3])
        bs_start_pos.append(split_line[4])
        shape.append(split_line[5].replace('hg38.', '') + '_' + 'score')
        score.append(split_line[6])

    shape_scores_df['bs'] = bs_li
    shape_scores_df['chr'] = chr_li
    shape_scores_df['start_pos'] = bs_start_pos
    shape_scores_df['shape'] = shape
    shape_scores_df['score'] = score

    shape_scores_df = shape_scores_df.sort_values(['bs','start_pos', 'shape'],
                                          ascending=[True, True, True]).reset_index(drop = True)

    shape_scores_df = shape_scores_df.pivot_table(index = ['bs', 'chr', 'start_pos'], columns = 'shape', values = 'score',
              aggfunc='first')
    shape_scores_df = shape_scores_df.reset_index(level=0).reset_index(level=0).reset_index(level=0)
    shape_scores_df['start_pos'] = shape_scores_df['start_pos'].astype('int')
    data_df['bs1_start_pos'] = data_df['bs1_start_pos'].astype('int')
    data_df['bs2_start_pos'] = data_df['bs2_start_pos'].astype('int')

    data_df['bs1'] = data_df['motif1'] + '_' + data_df['bs1_seq']
    data_df['bs2'] = data_df['motif2'] + '_' + data_df['bs2_seq']

    data_df = pd.merge(data_df, shape_scores_df, how = 'left',
         left_on = ['bs1', 'bs1_start_pos', 'chromosome'],
         right_on = ['bs', 'start_pos', 'chr'])

    data_df = pd.merge(data_df, shape_scores_df, how = 'left',
         left_on = ['bs2', 'bs2_start_pos', 'chromosome'],
         right_on = ['bs', 'start_pos', 'chr'])

    # print(shape_scores_df.head())
    # print(data_df.head())
    # print(data_df.columns)
    # print(data_df.head())

    return data_df

def extract_features(data_df):

    data_df = pd.merge(data_df, protein_df,  how='left', left_on=['motif1','motif2'],
                  right_on = ['protein_name_x','protein_name_y'])
    data_df.drop(['protein_name_x', 'protein_name_y'],
                axis=1, inplace= True)
    data_df.rename(columns = {'combined_score' : 'ppi_score'}, inplace = True)
    data_df['ppi_score'] = data_df['ppi_score'].replace(np.nan, 0.01)

    # at-gc skew score generation
    combined_at_skew = []
    combined_gc_skew = []
    at_skew1 = []
    gc_skew1 = []
    at_skew2 = []
    gc_skew2 = []

    for ix, row, in data_df.iterrows():

        gc, at = get_skew_score(row['bs1_seq'] + row['bs2_seq'])
        combined_at_skew.append(at)
        combined_gc_skew.append(gc)

        gc, at = get_skew_score(row['bs1_seq'])
        gc_skew1.append(round(gc, 2))
        at_skew1.append(round(at, 2))

        gc, at = get_skew_score(row['bs2_seq'])
        gc_skew2.append(round(gc, 2))
        at_skew2.append(round(at, 2))

    data_df['combined_at_skew'] = combined_at_skew
    data_df['combined_gc_skew'] = combined_gc_skew
    data_df['at_skew1'] = at_skew1
    data_df['gc_skew1'] = gc_skew1
    data_df['at_skew2'] = at_skew2
    data_df['gc_skew2'] = gc_skew2

    # DBD family

    data_df = pd.merge(data_df, dbd_df,  how='left', left_on=['motif1'],
                      right_on = ['Symbol'])
    data_df = pd.merge(data_df, dbd_df,  how='left', left_on=['motif2'],
                      right_on = ['Symbol'])
    data_df.drop(['Symbol_x', 'Symbol_y'],
                axis=1, inplace= True)
    data_df.rename(columns = {'Family_x' : 'dbd1', 'Family_y' : 'dbd2'}, inplace = True)

    # DNA Shape scores
    print('Generating unique motif positions...')
    all_positions = generate_unique_positions(data_df)
    print('Extracting shape scores...')
    extract_shape_scores(all_positions)
    print('Transforming shape scores...')
    data_df = attach_shape_scores(data_df.copy())

    return data_df


def feature_transformation(data_df):

    data_df.drop(['bs1_seq','bs1_start_pos', 'bs2_seq','bs2_start_pos', 'strand',
                    'dbbs', 'dng', 'gene_start_pos', 'bs1', 'bs2',
                    'start_pos_x', 'chr_x', 'bs_x',
                    'start_pos_y', 'chr_y', 'bs_y'],
            axis=1, inplace= True)

    print(data_df.columns)

    with open('./models/model_3/transformers.pickle', 'rb') as handle:
        transformers = pickle.load(handle)

    print('Loaded data transformer...')

    le1 = transformers['chromosome']
    le2 = transformers['motif1']
    le3 = transformers['motif2']
    le4 = transformers['dbd1']
    le5 = transformers['dbd2']
    le6 = transformers['ng']

    data_df['chromosome'] = le1.transform(data_df['chromosome'])
    data_df['motif1'] = le2.transform(data_df['motif1'])
    data_df['motif2'] = le3.transform(data_df['motif2'])
    data_df['dbd1'] = le4.transform(data_df['dbd1'])
    data_df['dbd2'] = le5.transform(data_df['dbd2'])
    data_df['ng'] = le6.transform(data_df['ng'])
    # print(data_df.columns)

    scaler = joblib.load('./models/model_3/scaler.scaler')
    print('Loaded data scaler...')
    data_df_scaled = scaler.transform(data_df.astype(np.float64))

    return data_df_scaled

def predict_pairs(data_df_scaled, data_df):

    model = keras.models.load_model('./models/model_3/ANN_model.model')
    preds  = model.predict(data_df_scaled)
    classes = ['co_occurring' if pred <= 0.5 else 'non_co_occurring' for pred in preds]
    co_occurring_score = [round(float(1 - pred), 3) for pred in preds]
    data_df['predictions'] = classes
    data_df['co-occur_score'] = co_occurring_score
    data_df = data_df[(data_df['predictions'] == 'co_occurring')].reset_index(drop = True)

    return data_df

def get_rightCRC(motif, df1):
    df1 = df1.reset_index(drop = True)
    df1 = df1[df1['bs1'] == motif]
    if not df1.shape[0]:
        CRC = []
        score = []
        return CRC, score
    scanned = []
    for ix, row in df1.iterrows():
        motif1 = row['bs1']
        motif2 = row['bs2']

        if motif1 not in scanned:
            CRC = []
            score = []
            df2 = df1[df1['bs1'] == motif1]
            max_score = max(df2['co-occur_score'])
            selected_motif = df2[df2['co-occur_score'] == max_score].iloc[0]['bs2']
    #         print(df2)
            CRC.append(selected_motif)
            score.append(max_score)
            next_search_index = max(list(df2.index)) + 1
            if df1[next_search_index:].shape[0]:
                new_CRC, new_score = get_rightCRC(selected_motif, df1[next_search_index:])
                CRC.extend(new_CRC)
                score.extend(new_score)
            else:
                CRC.extend([])
                score.extend([])
            scanned.append(motif1)
    
        return CRC, score
    
def get_leftCRC(motif1, df2, df1):
    CRC = []
    score = []
    max_score = max(df2['co-occur_score'])
    selected_motif = df2[df2['co-occur_score'] == max_score].iloc[0]['bs1']
    CRC.append(selected_motif)
    score.append(max_score)
    
    df2 = df1[df1['bs2'] == selected_motif]
#     print(selected_motif)
#     print(df2.shape[0])
    if df2.shape[0]:
        new_CRC, new_score = get_leftCRC(selected_motif, df2.copy(), df1.copy())
        new_CRC.extend(CRC)
        new_score.extend(score)
        CRC = new_CRC.copy()
        score = new_score.copy()
    else:
        return CRC, score
    
    return CRC,score
    

def get_CRCs(df1):
    
#     scanned = []
    all_CRCs = []
    all_scores = []
    
    for ix, row in df1.iterrows():
        motif1 = row['bs1']
        motif2 = row['bs2']
        co_score = row['co-occur_score']

#         if motif1 not in scanned:
#         print(motif1)
        CRC = []
        score = []
        df2 = df1[df1['bs1'] == motif1]
        max_score = max(df2['co-occur_score'])
        selected_motif = df2[df2['co-occur_score'] == max_score].iloc[0]['bs2'] 
#         print(df2)
        CRC.append(motif1)
        CRC.append(motif2)
        score.append(co_score)
        next_search_index = max(list(df2.index)) + 1
        df2 = df1[df1['bs2'] == motif1]
        if df2.shape[0]:
#             print(df1)
            new_CRC, new_score = get_leftCRC(motif1, df2.copy(), df1.copy())
            new_CRC.extend(CRC)
            new_score.extend(score)
            CRC = new_CRC.copy()
            score = new_score.copy()

        if df1[next_search_index:].shape[0]:
#             print(motif1)
#             print(df1[next_search_index:])
            new_CRC, new_score = get_rightCRC(selected_motif, df1[next_search_index:].copy())
            CRC.extend(new_CRC)
            score.extend(new_score)
        else:
            CRC.extend([])
            score.extend([])
#         scanned.append(motif1)
        all_CRCs.append(CRC)
        all_scores.append(round(np.mean(score),3))
    return all_CRCs, all_scores

def remove_duplicate_CRCs(CRCs, scores, first = 1):
    for ix in range(len(CRCs)):
        
        for jx in range(len(CRCs)):
            if not jx > ix:
                continue
            
            try:
                if all(motif in CRCs[ix] for motif in CRCs[jx]): # Checking if CRC2 is a subset of CRC1
                    del CRCs[jx]
                    del scores[jx]
            except:
                continue
                
            try:
                if all(motif in CRCs[ix] for motif in CRCs[jx]): # Checking if CRC1 is a subset of CRC2
                    del CRCs[ix]
                    del scores[ix]
            except:
                continue
    if first == 1:
        CRCs, scores = remove_duplicate_CRCs(CRCs, scores, 2)
    
    return CRCs, scores


def generate_crc(predictions_df, output_filepath):

    putative_CRC = pd.DataFrame(columns = ['gene_name', 'cluster_motifs', 'CRC_score'])
    all_ngs = set(predictions_df['ng'].to_list())

    with open(output_filepath, 'w') as fp:
        
        ngs = []
        gene_CRCs = []
        probs = []
        
        for ix, gene in tqdm(enumerate(all_ngs)):
            df1 = predictions_df[predictions_df['ng'] == gene]
            df1 = df1.reset_index(drop = True)

            CRCs, scores = get_CRCs(df1.copy())
            CRCs, scores = remove_duplicate_CRCs(CRCs, scores)

            ngs.extend([gene] * len(CRCs))
            gene_CRCs.extend(CRCs)
            probs.extend(scores)
            
            # IGV lines
            unique_dict = {}
            for jx, row in df1.iterrows():
                unique_dict[row['bs1']] = row['bs1_start_pos']
                unique_dict[row['bs2']] = row['bs2_start_pos']
            
            chromosome = df1.iloc[0]['chromosome']
            ng = df1.iloc[0]['ng']
            ng_start = df1.iloc[0]['gene_start_pos']
            gene_data = gene_data_df[(gene_data_df['gene_name'] == ng) & 
                    (gene_data_df['chromosome'] == chromosome) &
                    (gene_data_df['position_start'] == ng_start)].iloc[0]
            ng_end = gene_data['position_end']
            strand = gene_data['strand']
            
            for jx, CRC in enumerate(CRCs):
                
                r = randint(0,255)
                g = randint(0,255)
                b = randint(0,255)
                prob = scores[jx]
    #             print(CRC, prob)
                
                for kx, bs in enumerate(CRC):
                    start_pos = unique_dict[bs]
                    line = chromosome + '\t' + str(start_pos) + '\t' + \
                        str(start_pos + len(bs.split('_')[1])) + '\t' + bs.split('_')[0] + '\t' + str(prob) +'\t' + strand + '\t' + str(start_pos) + \
                        '\t' + str(start_pos + len(bs.split('_')[1])) + '\t' + str(r) + ',' + str(g) + ',' + str(b) + '\n' 
    #                 print(line)
                    fp.writelines(line)
                    
                line = chromosome + '\t' + str(ng_start) + '\t' + \
                        str(ng_start) + '\t' + 'gene_' + ng + '\t' + str(prob) +'\t' + strand + '\t' + \
                        str(ng_start) + '\t' + str(ng_start) + '\t' + str(r) + ',' + str(g) + ',' + str(b) + '\n' 
    #             print(line)
                fp.writelines(line)
                
    #         if not ix:
    #             break
        
        putative_CRC['gene_name'] = ngs
        putative_CRC['cluster_motifs'] = gene_CRCs
        putative_CRC['CRC_score'] = probs

        # putative_CRC.to_csv('../data/all_genes_train_predictions_CRC2.csv', index = False)


    return putative_CRC

