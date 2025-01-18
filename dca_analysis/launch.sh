#!/bin/bash

#SBATCH --partition=EPYC
#SBATCH --job-name=conformations
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=10
#SBATCH --mem-per-cpu=2g
#SBATCH --time=50:00:00

date

source ~/anaconda3/etc/profile.d/conda.sh

conda activate dca

input_file=$1

proteins=($(cat '../input_files/'$input_file | awk '{print $1}' ))

for name in "${proteins[@]}"
do
	bash scripts/run_dca.sh $name

done

date
