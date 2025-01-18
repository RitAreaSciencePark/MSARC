#!/bin/bash

#SBATCH --partition=DGX
#SBATCH --job-name=conformations
#SBATCH --nodes=1
#SBATCH --gpus-per-task=1
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=50
#SBATCH --mem-per-cpu=2g
#SBATCH --time=50:00:00

date

source ../../basic/bin/activate
#source /u/area/vpiomponi/scratch/env_dgx/bin/activate

input_file=$1

proteins=($(cat '../input_files/'$input_file | awk '{print $1}' ))

for name in "${proteins[@]}"
do

	python scripts/ohe_distances.py $name
	python scripts/ahc_clustering_seqs.py $name
	python scripts/dbscan.py $name
	bash scripts/cluster_AF.sh $name "dbscan_clusters"
        bash scripts/cluster_AF.sh $name "dbscanseq_clusters"
	bash scripts/cluster_AF.sh $name "ohe_ahc_clusters" 	

done

date
