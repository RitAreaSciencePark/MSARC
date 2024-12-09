from Bio import SeqIO
import os
import sys
import json
import numpy as np
import pandas as pd
import mdtraj as md
import matplotlib.pyplot as plt

def calculate_rmsd_mda(path_clusters, pdb_ref_path, high_ids):

    clusters = []

    for filename in os.listdir(path_clusters):
        if filename.startswith('clus') and filename.endswith('.pdb'):
            cluster = md.load(os.path.join(path_clusters, filename))
            clusters.append(cluster)
    trajectory = clusters[0]
    for cluster in clusters[1:]:
        trajectory += cluster

    pdb_ref = md.load(pdb_ref_path)

    backbone_ref=[]
    with open(pdb_ref_path, 'r') as file:
        for index, line in enumerate(file):
            columns = line.strip().split()
            if len(columns) >= 4 and columns[2] == "N":
                backbone_ref.append(index+1)

    filters = high_ids
    rmsd = md.rmsd(trajectory, pdb_ref, atom_indices=np.array(backbone_ref)[filters], ref_atom_indices=np.array(backbone_ref)[filters])

    return rmsd

def main(name):

    base_path = 'output_files/'
    path_full =  base_path + name + '/AF_full/'
    path_clusters =  base_path + name + '/AF_clusters/'
    output =  base_path + name + '/results/'
    ref_pdb = output + 'fullMSA_noH.pdb'

    plddt = []
    size = []
    clu_ids = os.listdir(path_clusters)
    sorted_clu_ids = sorted(clu_ids, key=lambda x: int(x.split('_')[-1]) if '_' in x and x.split('_')[-1].isdigit() else float('inf'))

    for clu_id in sorted_clu_ids:

        path_cluster = path_clusters + clu_id +'/'
        path_msa = base_path + name + '/clusters/' + clu_id + '.fasta'

        cluster_pdb = path_clusters + clu_id + '/' + [file for file in os.listdir(path_cluster) if '_relaxed_rank_001' in file][0]

        plddt_val, high_ids = calculate_plddt(path_cluster, path_full)
        plddt.append(plddt_val)
        size.append(count_sequences_in_fasta(path_msa))

    rmsd = calculate_rmsd_mda(output, ref_pdb, high_ids)

    np.save(output+'rmsd.npy', rmsd)
    np.save(output+'plddt.npy', plddt)
    np.save(output+'size.npy', size)

    plot(sorted_clu_ids, rmsd, plddt, size, name)

    return sorted_clu_ids, rmsd, plddt, size

def calculate_plddt(path_clusters, path_full):

    plddt_file = path_clusters + [file for file in os.listdir(path_clusters) if '_scores_rank_001' in file][0]
    with open(plddt_file, 'r') as file:
        result_data = json.load(file)

    ref_plddt_file = path_full + [file for file in os.listdir(path_full) if '_scores_rank_001' in file][0]
    with open(ref_plddt_file, 'r') as file:
        ref_data = json.load(file)

    plddt_local = result_data['plddt']
    plddt_avg = np.mean(plddt_local)
    high_ids = np.where(np.array(ref_data['plddt']) > 60)

    return plddt_avg, high_ids

def count_sequences_in_fasta(path_msa):
    sequence_count = int(sum(1 for _ in SeqIO.parse(path_msa, "fasta")))
    return sequence_count

def plot(clu_ids, rmsd, plddt, size, name):
    os.makedirs('figures', exist_ok=True)

    fig, ax = plt.subplots(figsize=(7,4))

    sc = plt.scatter(clu_ids, rmsd, cmap='rainbow_r', s=size, c=plddt)
    cbar = plt.colorbar(sc, ax=ax, pad=0.02, label='plDDT')
    plt.title(name)
    plt.xlabel('cluster_id')
    plt.ylabel('RMSD from full MSA AlphaFold2 prediction')
    plt.xticks(rotation=90)
    plt.grid(True, which='both', axis='both', color='gray', linestyle='--', linewidth=0.4)
    plt.xlim(left=-1,right=len(rmsd)+0.2)

    plt.tight_layout()
    plt.show()
    fig.savefig('figures/' + name+'_from_fullAF.png',dpi=500, format='png')

def max_size_alternative_cluster(name, ids, rmsd, plddt, size):
    maxx = 0
    max_clu, max_rmsd, max_plddt = None, None, None
    for i, id_clu in enumerate(ids):
        
        if rmsd[i] > 0.5 and plddt[i] > 65: # customize based on system
            
            if size[i] > maxx:
                maxx = size[i]
                max_clu = id_clu
                max_rmsd = rmsd[i]
                max_plddt = plddt[i]
                
    df = pd.DataFrame([[max_clu, maxx, max_rmsd, max_plddt]], columns=['cluster','size','rmsd','plddt'])
    print(df.to_string(index=False))
    out_file_name = 'output_files/' + name + '/results/max_size_alternative_cluster.csv'
    df.to_csv(out_file_name, index = False)


name = str(sys.argv[1])
    
ids, rmsd, plddt, size = main(name)
max_size_alternative_cluster(name, ids, rmsd, plddt, size)

