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


source /u/area/vpiomponi/scratch/env_dgx/bin/activate

names=($(cat ../input_files/systems | awk '{print $1}' | head -n 3))

for name in "${names[@]}"
do
	python scripts/sample_seeds.py $name
	srun bash scripts/MSA-Transformer_reps_dist.sh $name
	srun python scripts/correlation_samples_dist.py $name 
done
