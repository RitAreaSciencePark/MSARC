import numpy as np
import os
import sys
from sklearn.metrics.pairwise import pairwise_distances

name = str(sys.argv[1])
dir_in = str(sys.argv[2])
out_dir = name + '/reps_MSATransformer/' + dir_in +'/'


def collect_reps_ids(out_dir):
    
    msa_list = os.listdir(out_dir + 'reps/')
    alls = []
    idxs = []
    for i, msa_file in enumerate(msa_list):

        msa = np.load(out_dir + 'reps/' + msa_file)[0]
        ids = np.load(out_dir + 'ids/' +  msa_file)

        if i == 0:
            alls.append(msa[:,1:,:])
            idxs.append(list(ids))
        else:
            alls.append(msa[1:,1:,:])
            idxs.append(list(ids[1:]))

    all_msa = np.array([b for sys in alls for b in sys])
    all_ids = np.array([b for sys in idxs for b in sys])
    np.save(out_dir + 'all_reps.npy', all_msa)
    np.save(out_dir + 'all_ids.npy', all_ids)

    return all_msa, all_ids


#all_msa = np.load(out_dir + 'all_reps.npy')

# !!! you should really uncomment the previous and comment the following line if you already have REPS
all_msa, _ = collect_reps_ids(out_dir)
all_msa = all_msa.reshape(all_msa.shape[0],-1)
all_msa_scaled = (all_msa - all_msa.mean()) / all_msa.std() 

dist = pairwise_distances(all_msa_scaled, all_msa_scaled, metric='euclidean', n_jobs=-1)
np.save(out_dir + 'dist.npy', dist)



