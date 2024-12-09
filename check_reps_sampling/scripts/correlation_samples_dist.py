import numpy as np
import pandas as pd
import os
import sys
from scipy.stats import pearsonr, spearmanr
from multiprocessing import Pool



def read_dist_ids(pdb):
    
    path = pdb + '/reps_MSATransformer/'
    matrix_dir = os.listdir(path)
    
    matrices = []
    ids_merg = []
    for i,m in enumerate(matrix_dir):
        matrix = np.load(path + m + '/dist.npy') 
        ids = []
        for j,name in enumerate(os.listdir(path + m + '/reps/')):
            if j == 0:
                ids.append(np.load(path + m + '/ids/'+ name))
            else:
                ids.append(np.load(path + m + '/ids/'+ name)[1:])
        matrices.append(matrix)
        ids_merg.append([id_m for id_m in ids])

    return matrices, ids_merg



def order_matrices(matrices, ids_merg):
    
    matrix_ref = matrices[0]
    ids_ref = [val for idx in ids_merg[0] for val in idx]
    
    ordered = []
    triu_ids = np.triu_indices(matrix_ref.shape[0], k=1) 
    ordered.append(matrix_ref[triu_ids].flatten())
    
    for i in range(1,len(matrices)):
        
        ids_no_order = [val for idx in ids_merg[i] for val in idx]
        indices = [ids_no_order.index(item) for item in ids_ref]
        sel_matrix = matrices[i]
        ordered_matrix = sel_matrix[indices,:][:,indices]
        
        triu_ids = np.triu_indices(ordered_matrix.shape[0], k=1) 
        ordered.append(ordered_matrix[triu_ids].flatten())

    return ordered[:30]


def compute_spearman(args):
    pair, ordered = args
    i, j = pair
    return spearmanr(ordered[i], ordered[j]).correlation

def spearmanr_pairs(ordered):
    rows = len(ordered)
    pairs = [(i, j) for i in range(rows-1) for j in range(i+1, rows)]

    with Pool(processes=100) as pool:
        corrs = pool.map(compute_spearman, [(pair, ordered) for pair in pairs])

    return corrs


pdb = str(sys.argv[1])

matrices, ids_merg = read_dist_ids(pdb)
ordered = order_matrices(matrices, ids_merg)
corrs = spearmanr_pairs(ordered)

with open(pdb +'/corr_dist_result.txt', 'w') as f:
    f.write(str(pdb)+' mean Spearmanr: '+str(np.mean(corrs))+' std Spearmanr: '+str(np.std(corrs))+'\n')

