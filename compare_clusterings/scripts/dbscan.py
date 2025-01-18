import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import sys
import pandas as pd
from sklearn.cluster import DBSCAN
from Bio import SeqIO

prot = str(sys.argv[1])
seqs_dista = np.load('output_files/'+prot+'/seqs_dist.npy')
reps_dista = np.load('../output_files/'+prot+'/reps_MSATransformer/dist.npy')
msa_file = '../output_files/' + prot + '/sequence_files/full_MSA.fasta'
clu_out_seqs = 'output_files/'+ prot +'/dbscanseq_clusters/'
clu_out_reps = 'output_files/'+ prot +'/dbscan_clusters/'

def search_epsilon(dista, epsilon_range):
    max_clus = 0
    max_eps = None

    for ep in list(epsilon_range):
        clustering = DBSCAN(min_samples=20, eps=ep, metric='precomputed')
        clusters = clustering.fit_predict(dista)

        clus_number = len(list(set(clusters)))
        if clus_number > max_clus:
            max_clus = clus_number
            max_eps = ep
    return float(max_eps)

def save_clusters(prot, msa_file, dista, max_eps, clu_out):

    sequences_dict = {}
    for record in SeqIO.parse(msa_file, "fasta"):
        sequences_dict[record.id] = str(record.seq)

    clustering = DBSCAN(min_samples=20, eps=max_eps, metric='precomputed')
    nodes = clustering.fit_predict(dista)

    if not os.path.exists(clu_out):
        os.makedirs(clu_out)

    clusters = list(set(nodes))
    for c in clusters:
        indices, = np.where(nodes == c)
        if c>-1 and len(indices) >= 10:
            sub_ids = [ids[i] for i in indices]
            file = open(clu_out + "cluster_"+str(c+1)+'.fasta','w')
            for sub_id in sub_ids:
                if sub_id in sequences_dict:
                    file.write(f">{sub_id}\n{sequences_dict[sub_id]}\n")
            file.close()

epsilon_range_seqs = np.arange(1,30,1)
max_eps_seqs = search_epsilon(seqs_dista, epsilon_range_seqs)
save_clusters(prot, msa_file, seqs_dista, max_eps_seqs, clu_out_seqs)

epsilon_range_reps = np.arange(100,300,5)
max_eps_reps = search_epsilon(reps_dista, epsilon_range_reps)
save_clusters(prot, msa_file, reps_dista, max_eps_reps, clu_out_reps)
