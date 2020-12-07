import os
import subprocess
import tensorflow as tf
import numpy as np
import logging
from django.conf import settings
from tqdm import tqdm
from subprocess import Popen
from utils.FastaMLtoSL import FastaMLtoSL
from utils.utils import create_tfr_files, prob_to_secondary_structure

def predict(fasta_id, uid):
    venvPath = os.path.join(settings.SPOTRNA_ROOT, '.venv/bin/python')
    spotrnaPath = os.path.join(settings.SPOTRNA_ROOT, 'SPOT-RNA.py')
    outputPath = os.path.join(settings.BASE_DIR, 'static', 'tmp', uid)
    inputPath = os.path.join(outputPath, uid + '.fasta')
    ctFilePath = os.path.join(outputPath, fasta_id + '.ct')
    radiateImagePath = os.path.join(outputPath, fasta_id + '_radiate.png')
    lineImagePath = os.path.join(outputPath, fasta_id + '_line.png')
    try:
        if not os.path.isfile(ctFilePath):
            p = subprocess.Popen([venvPath, spotrnaPath, '--inputs', inputPath, '--outputs', outputPath], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
        if not os.path.isfile(radiateImagePath):
            subprocess.Popen(["java", "-cp", settings.SPOTRNA_ROOT + "/utils/VARNAv3-93.jar", "fr.orsay.lri.varna.applications.VARNAcmd", '-i', ctFilePath, '-o', radiateImagePath, '-algorithm', 'radiate', '-resolution', '8.0', '-bpStyle', 'lw'], stderr=subprocess.STDOUT, stdout=subprocess.PIPE, cwd=settings.SPOTRNA_ROOT).communicate()
        if not os.path.isfile(lineImagePath):
            subprocess.Popen(["java", "-cp", settings.SPOTRNA_ROOT + "/utils/VARNAv3-93.jar", "fr.orsay.lri.varna.applications.VARNAcmd", '-i', ctFilePath, '-o', lineImagePath, '-algorithm', 'line', '-resolution', '8.0', '-bpStyle', 'lw'], stderr=subprocess.STDOUT, stdout=subprocess.PIPE, cwd=settings.SPOTRNA_ROOT).communicate()
    except Exception as e:
        logging.error(e)
    return os.path.basename(radiateImagePath), os.path.basename(lineImagePath)

def predictSecondaryStructure(uid, baseDir):
    outputPath = os.path.join(baseDir, 'static', 'tmp', uid)
    fastaPath = os.path.join(outputPath, uid + '.fasta')
    FastaMLtoSL(fastaPath)
    input_file = os.path.basename(fastaPath)
    create_tfr_files(fastaPath, outputPath, input_file)
    with open(fastaPath) as file:
        input_data = [line.strip() for line in file.read().splitlines() if line.strip()]
    count = int(len(input_data)/2)
    ids = [input_data[2*i].replace(">", "") for i in range(count)]
    sequences = {}
    for i,I in enumerate(ids):
        sequences[I] = input_data[2*i+1].replace(" ", "").upper().replace("T", "U")

    # os.environ["CUDA_VISIBLE_DEVICES"]= str(args.gpu)
    #os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
    NUM_MODELS = 1

    test_loc = [os.path.join(outputPath, 'input_tfr_files', input_file+'.tfrecords')]

    outputs = {}
    mask = {}
    def sigmoid(x):
        return 1/(1+np.exp(-np.array(x, dtype=np.float128)))

    for MODEL in range(NUM_MODELS):

        # if args.gpu==-1:
        config = tf.compat.v1.ConfigProto(intra_op_parallelism_threads=16, inter_op_parallelism_threads=16)
        # else:
        #     config = tf.compat.v1.ConfigProto()
        #     config.allow_soft_placement=True
        #     config.log_device_placement=False
            
        print('\nPredicting for SPOT-RNA model '+str(MODEL))
        with tf.compat.v1.Session(config=config) as sess:
            saver = tf.compat.v1.train.import_meta_graph(os.path.join('linc2function/SPOT-RNA-models', 'model' + str(MODEL) + '.meta'))
            saver.restore(sess,os.path.join('linc2function/SPOT-RNA-models', 'model' + str(MODEL)))
            graph = tf.compat.v1.get_default_graph()
            init_test =  graph.get_operation_by_name('make_initializer_2')
            tmp_out = graph.get_tensor_by_name('output_FC/fully_connected/BiasAdd:0')
            name_tensor = graph.get_tensor_by_name('tensors_2/component_0:0')
            RNA_name = graph.get_tensor_by_name('IteratorGetNext:0')
            label_mask = graph.get_tensor_by_name('IteratorGetNext:4')
            sess.run(init_test,feed_dict={name_tensor:test_loc})
            
            pbar = tqdm(total = count)
            while True:
                try:        
                    out = sess.run([tmp_out,RNA_name,label_mask],feed_dict={'dropout:0':1})
                    out[1] = out[1].decode()
                    mask[out[1]] = out[2]
                    
                    if MODEL == 0:
                        outputs[out[1]] = [sigmoid(out[0])]
                    else:
                        outputs[out[1]].append(sigmoid(out[0]))
                    #print('RNA name: %s'%(out[1]))
                    pbar.update(1)
                except:
                    break
            pbar.close()
        tf.compat.v1.reset_default_graph()


    RNA_ids = [i for i in list(outputs.keys())]
    ensemble_outputs = {}

    print('\nPost Processing and Saving Output')
    for i in RNA_ids:
        ensemble_outputs[i] = np.mean(outputs[i],0)
        print(ensemble_outputs[i])
        print(ensemble_outputs[i].shape)
        print(ensemble_outputs[i][0].shape)

if __name__ == '__main__':
    predictSecondaryStructure('a025776e-1d0f-45c5-819f-434f07d3b0bb', baseDir='/home/monash/minor_thesis/workspace/cidmirnaweb')
