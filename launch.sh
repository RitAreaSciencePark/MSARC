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

#export PATH="/path/to/your/localcolabfold/colabfold-conda/bin:$PATH"
export PATH="/u/area/vpiomponi/source-codes/localcolabfold/colabfold-conda/bin:$PATH"
source conformer/bin/activate
#source /u/area/vpiomponi/scratch/env_dgx/bin/activate

input_file=$1

proteins=($(cat 'input_files/'$input_file | awk '{print $1}'))

for name in "${proteins[@]}"
do
	seq=$(grep "$name" 'input_files/'$input_file | awk '{print $2}')
	
	bash pipeline/1_full_af.sh $name  $seq

	srun bash pipeline/2_MSA-Transformer_reps_dist.sh $name 
        
	bash pipeline/3_cluster_AF.sh $name
	
	python scripts/rmsd_from_full_AF.py $name

done

date
