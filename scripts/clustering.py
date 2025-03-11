from scipy.cluster.hierarchy import ward, fcluster
from scipy.spatial.distance import squareform
from Bio import SeqIO
import os
import sys
import numpy as np

name = sys.argv[1]
base_path = 'output_files/'
dista = np.load(base_path + name + '/reps_MSATransformer/dist.npy')
reps = np.load(base_path + name + '/reps_MSATransformer/all_reps.npy')
ids = np.load(base_path + name + '/reps_MSATransformer/all_ids.npy')

clu_out = base_path + name + "/clusters/"
if not os.path.exists(clu_out):
    os.makedirs(clu_out)

msa_file = base_path + name + '/sequence_files/full_MSA.fasta'

def search_minsize_clustering(dista, min_size=19):

    dist = squareform(dista)
    Z = ward(dist)

    maxxclust, clusters = None, None
    many_clusters = int(reps.shape[0] / 10) # start from very high number of clusters
    for maxx in range(many_clusters, 2, -1):
        
        nodes = list(fcluster(Z, maxx, criterion="maxclust"))
        unique_nodes = list(set(nodes))
        sample_counts = 0
        for n in unique_nodes:
            # stop when all clusters size is above minimum
            if nodes.count(n) > min_size:
                maxxclust = maxx
                clusters = nodes
                sample_counts += 1
        if sample_counts == len(unique_nodes):
            break

    return maxxclust, clusters

maxxclust, nodes = search_minsize_clustering(dista)

def save_clusters_to_fasta(nodes, clu_out, msa_file):
    # Read the full MSA sequences from the fasta file
    seqs = {record.id: str(record.seq) for record in SeqIO.parse(msa_file, "fasta")}
    
    with open(msa_file, 'r') as infile:
        header = infile.readline().strip()  
        sequence = infile.readline().strip()
    
    clusters = list(set(nodes))  
    for c in clusters:
        indices = [i for i, x in enumerate(nodes) if x == c]
        sub_seqs = [seqs[ids[i]] for i in indices if ids[i] in seqs]
        # Save the clustered sequences to separate FASTA files
        if sub_seqs:
            with open(clu_out + f"cluster_{c}.fasta", 'w') as out_file:
                out_file.write(header + '\n')
                out_file.write(sequence + '\n')
                for i, seq in enumerate(sub_seqs):
                    out_file.write(f">{ids[indices[i]]}\n{seq}\n")

save_clusters_to_fasta(nodes, clu_out, msa_file)

