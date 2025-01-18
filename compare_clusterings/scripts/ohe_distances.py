import numpy as np
import os
import sys
from Bio import SeqIO
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.preprocessing import OneHotEncoder

name = str(sys.argv[1])
msa_file = '../output_files/' + name + '/sequence_files/full_MSA.fasta'
out_dir = 'output_files/' + name + '/'
os.makedirs(out_dir, exist_ok=True)

ids = []
sequences = []
for record in SeqIO.parse(msa_file, "fasta"):
    ids.append(record.id)
    sequences.append(str(record.seq))

ids_array = np.array(ids)
np.save(out_dir + "seqs_ids.npy", ids_array)

sequences_array = np.array([list(seq) for seq in sequences])
encoder = OneHotEncoder(dtype=np.int32)
all_msa = encoder.fit_transform(sequences_array) #.flatten().reshape(-1, 1))

dist = pairwise_distances(all_msa,  metric='euclidean', n_jobs=-1)
np.save(out_dir + 'seqs_dist.npy', dist)



